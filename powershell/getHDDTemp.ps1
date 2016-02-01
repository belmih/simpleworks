$smtpServer = "192.168.255.4"
$serverName = "192.168.255.2"
[int] $max_temp = 50


$scriptName = $MyInvocation.MyCommand.Name
$logfilename = "$scriptname.log"

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

function sendEmail([string]$from,[string]$to,[string]$subject,[string]$body)
{
	$mailMess = New-Object System.Net.Mail.MailMessage($from,$to,$subject,$body)
	$smtp = New-Object Net.Mail.SmtpClient($smtpServer,25);
	$smtp.Send($mailMess);
}

$str_with_temp = @(./smartctl.exe -a /dev/sda | where {$_ -match "Temperature_Celsius"})

if ($str_with_temp.Length -ge 0)
{
	$curr_temp = [int]::Parse(@(@($str_with_temp[0].split('-'))[4].split('('))[0].Trim())

    to_log ("Температура диска на сервере $serverName: " + $curr_temp.ToString() + "°C");
    
	if ($curr_temp -ge $max_temp)
	{	
        [string] $message = "Температура диска на сервере " + $serverName + ": " + $curr_temp.ToString() + "°C";
        sendEmail "<server@srvmail.local>" "admin@srvmail.local" "***Temperature Warning***" $message;
        [string] $smsmessage = "Warning: 213 kabinet. Smart temperature value - " + $curr_temp.ToString() + " gr.";
        Out-File -FilePath "D:\Scripts\getTempAndAlarm\temp213.txt" -InputObject $smsmessage -Encoding ASCII;
        
        Start-Process -FilePath D:\Scripts\getTempAndAlarm\Scp_SshExec.exe -Wait -WindowStyle Normal -WorkingDirectory D:\Scripts\getTempAndAlarm
    }
}
