#!/usr/bin/perl
use DBI;
use CGI qw(:standard);
use LWP::Simple;

require "/home/weoms/proc/globals/connDB.pl";

$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbdate=`date '+%Y-%m-%d %H:%M:%S'`; chomp $dbdate;
my $ip = $ENV{'REMOTE_ADDR'};
if( $cgi->param()){
	( $user, $passwd)=( $cgi->param('username'),$cgi->param('passwd'));
	#print "$user $passwd - ";
	my $dbh=connCDMAdb(); 
	$st=qq{ select * from SIRusers where username='$user'};
	$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	@result =$sth->fetchrow_array ;
	$sth->finish;
	if($#result > 0) {
		if($result[3]) {
			my $url = qq{http://ftapp:8080/postsales/jsp/adAUTH.jsp?username=$user&password=$passwd};
			my $content = get($url) or $errmsg = "Error! Cannot communicate with Active Directory";
			#$content = "true";	
			if($content =~ m/true/i) {
				$st=qq{INSERT INTO SIRlogs VALUES('','$dbdate','$user','1','Logged in from $ip')};
			        $sth=$dbh->prepare($st) or print "Could not prepare on $st</br>";
			        $sth->execute() or print "could not execute $st</br>"; $sth->finish;
			        print "true";
			} 
			else {print "false"}
		}
		else {
			$st=qq{ select * from SIRusers where username='$user' and passwd=password('$passwd')};
			$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
			$sth->execute() or print "could not execute\n$!";
			@result =$sth->fetchrow_array ;
			$sth->finish;
			if($#result > 0) {
				$st=qq{INSERT INTO SIRlogs VALUES('','$dbdate','$user','1','Logged in from $ip')};
			        $sth=$dbh->prepare($st) or print "Could not prepare on $st</br>";
			        $sth->execute() or print "could not execute $st</br>"; $sth->finish;
				print "true";
			}
			else {print "false";}
		}
	}
	else {print "false";}
	$dbh->disconnect;

}
else{print "false";}
exit 0;