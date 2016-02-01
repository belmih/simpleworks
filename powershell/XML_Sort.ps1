# XML sorter
clear
$MDR_In = "C:\Portal\IN"
$MDR_Out = "C:\Portal\OUT"
# folders
$FTP_Folder = "C:\FTP"
$FTP_Kadastr = "C:\FTP_Kadastr"
#
$senderCode = "35.0.1.132"
$year = get-date -format 'yyyy'
$month = get-date -format 'MM'
$day = get-date -format 'dd'
# logs
$timestamp = get-date -format yyyyMMddHHmmss
$scriptname = $myInvocation.MyCommand.Name
$logFolder = "C:\AdminScripts\logs"
$logfilename = "$logFolder\$timestamp`_$scriptname.txt"
Function to_log
{
	Param ($message)
	Process
	{
		Foreach ($strmsg in $message)
		{
			$dt = get-date -format 'yyyy.MM.dd HH:mm:ss'
			$tmp = "[$dt] $strmsg"
			write-host $tmp 
			$tmp  | Out-File -FilePath $logfilename -Append -encoding UTF8
		}
	}
}
Function Test-Directory 
{
	Param
	(
		[parameter(Mandatory=$true)]
		[String]$folder
	)
	Process
	{
		if (-not (test-Path ($folder)))
		{
			New-Item -type Directory -Path $folder
		} 
	}
}
Function Copy-MyFile
{
	Param
	(
		[parameter(Mandatory=$true)]
		$file,
		[parameter(Mandatory=$true)]
		$destination
	)
	Process
	{
		Test-Directory($destination)
		to_log "Копируем файл: $file -> $destination"
		Copy-Item $file $destination -Force
	}
}
Function Backup-File
{
	Param
	(
		[parameter(Mandatory=$true)]
		[String]$file,
		[parameter(Mandatory=$true)]
		[String]$directory		
	)
	Process
	{
		$backupsFolder = $directory.Replace("C:\","C:\Backups\$year-$month-$day\")
		Test-Directory($backupsFolder)
		to_log "Перемещаем в архив: $file -> $backupsFolder"
		Move-Item $file $backupsFolder -Force
	}
}
Function Get-District
{
	Param ([String]$code, [String]$book)
	Process
	{
		$vologda_code = @("35-35-01", "35-0-1-132")
        $volrn_code = @("35-0-1-115")
        $nikolsk_code = @("35-35-16", "35-0-1-114")
        $gryazovets_code = @("35-35-28", "35-0-1-131")
		$sokol_code = @("35-35-26", "35-0-1-128")
        $cherrn_code = @("35-35-22","35-0-1-126")
		$district = $null
		#
		if ($vologda_code -contains $code)
		{
			if ([int]$book -lt 700)
			{
				# volrn
			}
			else
			{
				# vologda
			}
			$district = "vologda"
		}
		if ($sokol_code -contains $code)
		{
			$district = "sokol"
		}
		if ($cherrn_code -contains $code)
		{
			$district = "cherrn"
		}
		if ($gryazovets_code -contains $code)
		{
			$district = "gryazovets"
		}
		if ($nikolsk_code -contains $code)
		{
			$district = "nikolsk"
		}
		return $district
	}
}
function Sort-File
{
	Param ([String]$code, [String]$book, [String]$file, [String]$attach)
	Process
	{
		$district = Get-District $code $book
		if ($district)
		{
			to_log "Район: $district"
			$organization = "rosree"
			$kadastr_books = @("3011","3012","3013","3014","3015","4021","4022")
			if ($kadastr_books -contains $book)
			{
				$organization = "kadastr"
				Copy-MyFile $file $FTP_Kadastr
				if ($attach)
				{
					Copy-MyFile $attach $FTP_Kadastr
				}
			}
			to_log "Организация: $organization"
			$directory = "$FTP_Folder\$district\$organization\in\"
			Copy-MyFile $file $directory
			if ($attach)
			{
				Copy-MyFile $attach $directory
			}
			return $True
		}
		return $False
	}
}
Function Get-CodeBook
{
	Param([String]$number)
	Process
	{
		to_log "Номер: $number"
		$match = [regex]::Match($number,"^(.+?)/(\d+)/")
		$code = $match.Groups[1].Value
		$book = $match.Groups[2].Value
		return $code, $book
	}
}
Function Send-Email
{
	Param ([String]$message, [String]$attach)
	Process
	{
		# mail
		$compname = (Get-WMIObject Win32_ComputerSystem -computerName ".").name
		$from = "$compname <server@srvmail.local>"
		$to = "Админ <admin@srvmail.local>"
		$smtpServer = "mail.srvmail.local"
		$encoding = [System.Text.Encoding]::UTF8
		$subject = "$compname`: $scriptname"
		if (!$attach)
		{
			 Send-MailMessage -from $from -to $to `
			-subject $subject -body $message  `
			-encoding $encoding  -smtpServer $smtpServer
		} 
		else
		{
			 Send-MailMessage -from $from -to $to `
			-subject $subject -body $message  `
			-Attachments "$attach" -encoding $encoding  -smtpServer $smtpServer
		}
	}
}
Function Test-Attach
{
	Param([String]$attach)
	Process
	{
		if (-not (Test-Path($attach)))
		{
			to_log "$attach не найден!"
			Send-Email "ВНИМАНИЕ!!! Не найден Attach: $attach"
			Return $False
		}
		Return $True
	}
}
Function Set-Utf8NoBomEncoding
{
	Param($MyPath)
	Process
	{
		$MyFile = Get-Content $MyPath
		$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding($False)
		[System.IO.File]::WriteAllLines($MyPath, $MyFile, $Utf8NoBomEncoding)
	}
}
to_log "Hello!"
#
#
# -- OUT --
#
#
to_log "СОРТИРОВКА ИСХОДЯЩИХ ПАКЕТОВ"
Get-Childitem -Path $FTP_Folder | Where-Object {$_.PSIsContainer} | Foreach-Object {
	$folder = $_.FullName
	to_log "Обрабатываем каталог: $folder"
	$count = 0
	Get-Childitem -Path $folder -Recurse -Force -Include *.xml | Where-Object {$_.FullName -like '*\out\*'} | Foreach-Object {
		$count++
		$file = $_.FullName
		$fileName = $_.Name
		$directory = $_.DirectoryName
		$unknownXML = $True
		to_log $count
		to_log "Анализируем файл: $file"
		$xml = [xml](Get-Content -Encoding UTF8 $file)
		#
		if($xml.RegFolder.Info.Sender.Code) 
		{	
			to_log "Тип XML-файла: RegFolder.Info.Sender.Code + Attach"
			$attach = "$directory\" + $xml.RegFolder.Info.Attach.Name
			if (Test-Path($attach))
			{
				$recipientCode = $xml.RegFolder.Info.Recipient.Code
				to_log "Recipient.Code: $recipientCode"
				$recipientCode_OKATO = $xml.RegFolder.Info.Recipient.Code_OKATO
				to_log "Recipient.Code_OKATO: $recipientCode_OKATO"
				$number = $xml.RegFolder.Request.Number
				to_log "RegFolder.Request.Number: $number"
				$oldSenderCode = $xml.RegFolder.Info.Sender.Code
				to_log "Меняем Sender.Code: $oldSenderCode -> $senderCode"
				$xml.RegFolder.Info.Sender.Code = $senderCode
				Copy-MyFile $attach $MDR_Out
				$newXMLFile = "$MDR_Out\$fileName"
				to_log "Сохраняем измененный XML-файл как $newXMLFile"
				$xml.Save($newXMLFile)
				Backup-File $attach $directory
				Backup-File $file $directory
			} 
			else
			{
				to_log "$attach не найден!"
				Send-Email "ВНИМАНИЕ!!! Не найден Attach. `n $file `n $attach"
			}
			$unknownXML = $False
		}
		<#
		if($xml.DocumentStatus.Info.Sender.Code)
		{
			to_log "Тип XML-файла: DocumentStatus.Info.Sender.Code"
			$oldSenderCode = $xml.DocumentStatus.Info.Sender.Code
			to_log "Меняем Sender.Code: $oldSenderCode -> $senderCode"
			$xml.DocumentStatus.Info.Sender.Code = $senderCode
			$newXMLFile = "$MDR_Out\$fileName"
			to_log "Сохраняем измененный XML-файл как $newXMLFile"
			$xml.Save($newXMLFile)
			Backup-File $file $directory
			$unknownXML = $False
		}
		#>
		if ($unknownXML)
		{
			to_log "ВНИМАНИЕ!!! Неизвестный XML-файл!"
			Send-Email "ВНИМАНИЕ!!! Неизвестный XML-файл!" $file
		}
		to_log ""
	}
}
#
#
# -- IN --
#
#
to_log "СОРТИРОВКА ВХОДЯЩИХ ПАКЕТОВ"
to_log "Обрабатываем каталог: $MDR_In"
$count = 0
Get-Childitem -Path $MDR_In -Recurse -Force -Include *.xml | Foreach-Object {
	$count++
	$file = $_.FullName
	$directory = $_.DirectoryName
	$unknownXML = $True
	#
	to_log $count
	to_log "Анализируем файл: $file"
	$xml = [xml](Get-Content -Encoding UTF8 $file)
	
	if($xml.Status.Number)
	{
		to_log "Тип XML-файла: Status.Number"
		$code, $book = Get-CodeBook($xml.Status.Number)
		if(Sort-File $code $book $file)
		{
			Backup-File $file $directory
		}
		$unknownXML = $False
	}
	
	# Обратить внимание
	if ($xml.PackageStatus.Request)
	{
		to_log "Тип XML-файла: PackageStatus.Request.Number"
		$sorted = $False
		$xml.PackageStatus.Request | Foreach-Object {
			$code, $book = Get-CodeBook($_.Number)
			$sorted = Sort-File $code $book $file
		}
		if ($sorted)
		{
			Backup-File $file $directory
		}
		$unknownXML = $False
	}
	if ($xml.OutDocument.Request_Number)
	{
		to_log "Тип XML-файла: OutDocument.Request_Number + Attach"
		$attach = "$directory\" + $xml.OutDocument.Info.Attach.Name
		if (Test-Path($attach))
		{
			$code, $book = Get-CodeBook($xml.OutDocument.Request_Number)
			if(Sort-File $code $book $file $attach)
			{
				Backup-File $attach $directory
				Backup-File $file $directory
			}
		}
		$unknownXML = $False
	}
	<#
	if ($xml.PackageStatus.Note)
	{
		to_log "Тип XML-файла: PackageStatus.Note.Number"
		$sorted = $False
		$xml.PackageStatus.Request | Foreach-Object {
			$code, $book = Get-CodeBook($_.Number)
			$sorted = Sort-File $code $book $file
		}
		# Обратить внимание
		if ($sorted)
		{
			Backup-File $file $directory
		}
		$unknownXML = $False
	}
	#

	#
	if ($xml.DocumentStatus.Request_Number)
	{
		to_log "Тип XML-файла: DocumentStatus.Request_Number"
		$code, $book = Get-CodeBook($xml.DocumentStatus.Request_Number)
		if(Sort-File $code $book $file)
		{
			Backup-File $file $directory
		}
		$unknownXML = $False
	}
	#>
	if ($unknownXML)
	{
		to_log "ВНИМАНИЕ!!! Неизвестный XML-файл!"
		Send-Email "ВНИМАНИЕ!!! Неизвестный XML-файл!" $file
	}
	to_log ""
}
to_log "Done."
Start-Sleep -s 2
