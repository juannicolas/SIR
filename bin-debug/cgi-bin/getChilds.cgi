#!/usr/bin/perl
use CGI;

require "/home/weoms/proc/globals/connDB.pl";

my $cgi=new CGI;
print "Content-type: text/xml\n\n";

$outageId=$cgi->param('outageId');
$sirId=$cgi->param('sirId');

my $dbh=connCDMAdb();

my $st=qq{ select * from SIRtbl where id='$sirId'};
my $sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
$sth->execute() or print "could not execute\n$!";
my @result=$sth->fetchrow_array;
if($result[5] =~ /Fault/) {$table = "FaultAlarms";}
else {$table = "OtherAlarms";}

my $tmpXml = qq{
<?xml version="1.0" encoding="utf-8"?>
<Events>};
if($outageId > 0) {	
	$st=qq{ select id,neID,networkElement,startDate,description from $table where outageID='$outageId' or outageID2='$outageId'};
	$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	while(my(@result)=$sth->fetchrow_array){
		my @neFlds = split(":",$result[2]);
		my $ne = getNeName($result[1]);
		if($ne eq "") {$ne="Cell $result[1]";}
		$tmpXml .= qq{
	<event>
		<ne>$ne</ne>
		<startTime>$result[3]</startTime>
		<description><![CDATA[$result[4] - $neFlds[3]]]></description>
	</event>};
	}
	$sth->finish;
}
else{
	if($sirId <= 5) {$tmpsirId=1;}
	else {$tmpsirId=$sirId;}
	$st=qq{ select id,neID,networkElement,startDate,description from $table where sirID='$tmpsirId' and status='1'};
	$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	while(my(@result)=$sth->fetchrow_array){
		my @neFlds = split(":",$result[2]);
		my $ne = getNeName($result[1]);
		if($ne eq "Exclude") {next;}
		if($ne eq "") {$ne="Cell $result[1]";}
		$tmpXml .= qq{
	<event>
		<ne>$ne</ne>
		<startTime>$result[3]</startTime>
		<description><![CDATA[$result[4] - $neFlds[3]]]></description>
	</event>};
	}
	$sth->finish;
}
$dbh->disconnect;
$tmpXml .= qq{
</Events>};
print $tmpXml;
exit 0;

sub getNeName {
	my $ne = shift || die "Need NE ID\n";

	my $dbh=connWEDdb();
	my $st=qq{ select Name,Municipality from CellLocations where CellID='$ne'};
	my $sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	my @result=$sth->fetchrow_array;
	if($sirId == 4 || $sirId == 5) {
		my $isExcluded=excludeCity($city);
		if(!$isExcluded) {$ne = "$result[1] - Cell $ne $result[0]";}
		else {$ne = "Exclude";}
	}
	else {$ne = "Cell $ne $result[0]";}
	return $ne;
}

sub excludeCity {
	my $city=shift  || return 0;
	my $included = "San Juan Bayamon Carolina Caguas Guaynabo Ponce Arecibo";
	
	if($included =~ /$city/) {return 0;}
	else {return 1;}
}
	

