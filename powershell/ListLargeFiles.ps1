# List Large Files
# Example: ListLargeFiles.ps1 C:\Folder\ 100mb *.txt,*.bmp

Param (
    [parameter(Mandatory=$true)]
    [alias("f")]
    $targetFolder,
    [parameter(Mandatory=$true)]
    [alias("s")]
    $sizeFile,
	[parameter(Mandatory=$true)]
    [alias("e")]
    $extension)
  
cls	

$strComputer = "."
$scriptname = $myInvocation.MyCommand.Name
$timestamp = get-date -format yyyyMMddHHmmss
$logfilename = "$timestamp`_$scriptname.log"
$msg = ""

Function sendEmail([string]$to,[string]$subject,[string]$body,[string]$file)
{
    $from = 'server@mail.local'
    $message = New-Object System.Net.Mail.MailMessage($from, $to, $subject, $body)
    
    if ($file){
        $filenameAndPath = (Resolve-Path $file).ToString()
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

$compname = (Get-WMIObject Win32_ComputerSystem -computerName $strComputer ).name

$largefiles = Get-ChildItem -path $targetFolder -recurse -force -include $extension `
    | Where-Object {!$_.PSIsContainer -and ($_.Length -gt $sizeFile)} | Sort-Object -property Length -descending
        
foreach ($file in $largefiles)
{
    $FullName = $file.FullName
	$fileSize = "{0:N3}" -f ($file.Length/1mb)
    $msg += "{0} MB`t{1}`n" -f $fileSize, $FullName
}

if ($msg)
{
    sendEmail 'admin@mail.local' "Информация от $compname" "Результат выполнения $scriptname : Список файлов $extension в $targetFolder размером больше $sizeFile`n`n$msg"
}
