#!/usr/bin/perl
use CGI;

require "/home/weoms/proc/globals/connDB.pl";
require "/home/weoms/proc/globals/sendemail.pl";
require "/home/weoms/proc/globals/sendsms.pl";

my $currTime=`date '+%Y-%m-%d %H:%M:%S'`; chomp $currTime;
my $cgi=new CGI;
print "Content-type: text/html\n\n";

my $action=$cgi->param('action');
my $id=$cgi->param('eventId'); #same as sirId
my $outageId=$cgi->param('outageId');
my $user=$cgi->param('user');
my $message="No action needed";
my $dbh=connCDMAdb();
my $failed=0;

my $st=qq{ select * from SIRtbl where id='$id'};
my $sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
$sth->execute() or print "could not execute\n$!";
my @result=$sth->fetchrow_array;
if($result[5] =~ /Fault/) {$table = "FaultAlarms";}
else {$table = "OtherAlarms";}
#my $smsMsg = "SIR Alert\n$currTime\n\n";

if($action =~ /Activate/) {
	$st=qq{ select description from SIRtbl where id='$id'};
	$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	my $eventName =$sth->fetchrow_array;
	$st=qq{ select * from SIRoutages where sirID='$id' and status = '1'};
	$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	@result =$sth->fetchrow_array;
	if($#result > 0) {$message = "Error: Event is already active!";}
	else {
		$st=qq{insert into SIRoutages values('','$id','$currTime','','Manually activated','$user','1','100')};
		$sth=$dbh->prepare($st) or $failed=1;
		$sth->execute() or $failed=1;
		if($failed) {$message = "Error: Could not activate event!";}
		else{
			$st=qq{INSERT INTO SIRlogs VALUES('','$currTime','$user','2','Activated Event: $id')};
			$sth=$dbh->prepare($st) or print "Could not prepare on $st</br>";
			$sth->execute() or print "could not execute $st</br>";
			$message = "Event was activated at $currTime";
		}
		#$smsMsg .= "$eventName\n\n";
		#SendSMS("7876350681",$smsMsg);	#Lawrence
		#SendSMS("7876431020",$smsMsg);  #Bob
		#SendSMS("7876440999",$smsMsg);	#Hector	
		#SendSMS("7876081685",$smsMsg);	#Fernando
		#my $email = $smsMsg . "\nFor more information go to SIR Events Tab in the SIR Management Portal: http://thor/SIR/";
		#SendEmail("SIR","halvarez\@centennialpr.com,lmatta\@centennialpr.com,rcrawford\@centennialpr.com","","","SIR Alert: $currTime",$email);
	}
	$sth->finish;
}
elsif($action =~ /Clear/) {
	$st=qq{update SIRoutages set endDate='$currTime',notes='Manually cleared',modifiedBy='$user',status='0',meter='0' where id='$outageId'};
	$sth=$dbh->prepare($st) or $failed=1;
	$sth->execute() or $failed=1;
	if($failed) {$message = "Error: Could not clear event!";}
	else{
		$st=qq{INSERT INTO SIRlogs VALUES('','$currTime','$user','3','Cleared Event: $id')};
		$sth=$dbh->prepare($st) or print "Could not prepare on $st</br>";
		$sth->execute() or print "could not execute $st</br>";
		###Clear Child events
		$st=qq{update $table set endDate='$currTime',status='0' where outageID='$outageId' or outageID2='$outageId'};
		$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
		$sth->execute() or print "could not execute\n$!";
		$message = "Event was cleared at $currTime";
	}
	$sth->finish;
}
$dbh->disconnect;
system("perl /home/weoms/www/apps/SIR/cgi-bin/createXMLs.pl");

print $message;
exit 0;