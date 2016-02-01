# backup

cls

# folders
$backupsFolder = "D:\backups"
#$sourceFolder="C:\www"

# db
#$postgres_user = "backupadmin"
#$postgres_password = "9WJiWfgVZ1jcbs65wMDeCgs"
$pathtopgdump = "D:\PostgreSQL\9.1\bin\pg_dump.exe"
$pathtopgdumpall = "D:\PostgreSQL\9.1\bin\pg_dumpall.exe"

$databases = "postgres_roles", "vologda", "volrn", "cherrn", "nikolsk", "sokol", "gryazovets", "postgres_full_dump"
#$databases = "nikolsk"

# 7zip
$7zip = "C:\Program Files\7-Zip\7z.exe"

# log file
$timestamp = get-date -format yyyyMMddHHmmss
$scriptname = $myInvocation.MyCommand.Name
$logfilename = "$backupsFolder\$timestamp`_$scriptname.txt"

# for delete old files
$saveFilesCount = 14
$oldDays = 15

# error
$script_error = $False

$strComputer = "."


Function to_log($message)
{
    foreach ($strmsg in $message)
    {
        $dt = get-date -format 'yyyy.MM.dd HH:mm:ss'
        $tmp = "[$dt] $strmsg"
        write-host $tmp 
        $tmp  | Out-File -FilePath $logfilename -Append -encoding default
    }
}

# Получаем имя компьютера
$compname = (Get-WMIObject Win32_ComputerSystem -computerName $strComputer).name

# Создаем папку с архивами
if (-not (test-Path ($backupsFolder)))
{
    New-Item -type Directory -Path $backupsFolder
    to_log("Создали папку $backupsFolder")
}
else 
{
	# Удаляем старые файлы
	$files = Get-Childitem -Path $backupsFolder -Recurse -Force |
		Where-Object {!$_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-$oldDays)} |
		Where-Object {$_.FullName -notlike '*\.Sync*'} |
		Sort-Object CreationTime
	if ($files)
	{
		to_log("Старые файлы:`n$files`n")
		foreach ($file in $files) 
		{
			$mFiles = Get-Childitem -Path $backupsFolder -Recurse -Force |  Measure-Object
			$fCount = $mFiles.count
			if ( $fCount -gt $saveFilesCount)
			{
				to_log("Старых файлов $fCount...")
				to_log("Удаляем файл $file")
				$file | Remove-Item -force
			} 
			else
			{
				to_log("Старых файлов осталось всего $saveFilesCount")
				break
			}
		}	
	}
	else
	{
		to_log("Старых файлов нет")
	}
}

# Делаем дамп БД и архивируем
foreach ($db in $databases) 
{ 
    $timestamp = get-date -format yyyyMMddHHmmss
    $dt = get-date -format 'yyyy.MM.dd HH:mm:ss'
    $sqlfilename = "$backupsFolder\$timestamp`_$db`.backup"
    $archivefilename = "$timestamp`_$db`.backup.7z"
    
	if ($db -eq "postgres_roles")
	{
	   to_log("Дамп ролей сервера")
	   $output = @(( cmd /c " `"$pathtopgdumpall`" --host localhost --port 5432 --username `"postgres`" --no-password -r --file $sqlfilename") 2>&1 )
	}
	elseif ($db -eq "postgres_full_dump") 
	{
		to_log("Дамп всего сервера")
		$output = @(( cmd /c " `"$pathtopgdumpall`" --host localhost --port 5432 --username `"postgres`" --role `"postgres`" --no-password --verbose --file $sqlfilename") 2>&1 )
	}
	else
	{
	   to_log("Дамп $db")
       $output = @(( cmd /c " `"$pathtopgdump`" --host localhost --port 5432 --username `"postgres`" --no-password  --format custom --blobs --verbose --file $sqlfilename `"$db`"") 2>&1 )
    }

    $filelength = (Get-Item $sqlfilename).Length
#    if (($output -match "error") -or ($filelength -lt 1024) )
    if ($filelength -lt 1024)
    { 
        to_log("ОШИБКА: $output")
        $script_error = $True
    } 
	else
	{
        to_log("Архивируем...")
        $output = (( &$7zip a "$backupsFolder\$archivefilename" "$sqlfilename") 2>&1 )
        if (-not ($output -match "Everything Is OK"))
        {   
            to_log("ОШИБКА: $output")
            $script_error = $True
        }
		else
		{
            Remove-Item $sqlfilename
            to_log("Ok")
        }  
    }
}

# mail
$from = "$compname <server@srvmail.local>"
$to = "Админ <admin@srvmail.local>"
$smtpServer = "mail.srvmail.local"
$encoding = [System.Text.Encoding]::UTF8

if (!$script_error)
{
	send-mailmessage -from $from -to $to `
	-subject "$compname`: Хорошие новости" -body "Выполнен $scriptname"  `
	-Attachments "$logfilename" -encoding $encoding  -smtpServer $smtpServer
} 
else
{
	send-mailmessage -from $from -to $to `
	-subject "$compname`: Внимание! Ошибки!" -body "Ошибки при выполнении $scriptname" `
	-Attachments "$logfilename" -encoding $encoding  -smtpServer $smtpServer
}

Start-Sleep -s 2
