# DiscSpace
# Скрипт проверяет свободное место на диске
# При запуске пишет лог
# Если свободного места меньше 25% - отправляет сообщение на эл.почту

cls

$strComputer = "."
$scriptName = $MyInvocation.MyCommand.Name
$logfilename = "$scriptName.log"
$message = ""


function sendEmail([string]$to,[string]$subject,[string]$body,[string]$file)
{
    $from = 'server@srvmail.local'
    $message = New-Object System.Net.Mail.MailMessage($from, $to, $subject, $body)
    if ($file)
	{
        $filenameAndPath = (Resolve-Path .\$file).ToString()
        $attachment = New-Object System.Net.Mail.Attachment($filenameAndPath, 'text/plain')
        $message.Attachments.Add($attachment)
    }
	$smtpClient = New-Object System.Net.Mail.SmtpClient
	$smtpClient.host = '192.168.255.4'
    $smtpClient.Send($message)
}


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
$compname = "computer"
if ($args[0])
{
	$compname = $args[0];
} 
else
{
    $compname = (Get-WMIObject Win32_ComputerSystem -computerName $strComputer ).name
}
 

$colDisks = get-wmiobject Win32_LogicalDisk -computername $strComputer -Filter "DriveType = 3"
foreach ($objdisk in $colDisks) 
{	
    $dt = Get-Date -format "dd.MM.yyyy HH:mm:ss"
    $nameDisk = $objDisk.DeviceID
	$sizeDisk = "{0:N1}" -f ($objDisk.size/1gb)
	$freeSpace = "{0:N1}" -f ($objDisk.freespace/1gb)
	$percentFreeSpace = "{0:P0}" -f ([double]$objDisk.FreeSpace/[double]$objDisk.Size)
    $tmp = "На диске $nameDisk свободно $freeSpace Гб из $sizeDisk Гб ($percentFreeSpace)"
    to_log($tmp)
	if ($percentFreeSpace -lt 25)
	{
		$message += "[$dt] $tmp`n"
	}
}


if ($message)
{
	sendEmail 'admin@srvmail.local' "Внимание! Информация от $compname" "$message"
}
