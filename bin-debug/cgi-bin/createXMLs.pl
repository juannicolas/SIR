#!/bin/perl

require "/home/weoms/proc/globals/connDB.pl";

my $dbh=connCDMAdb();
createParentsXML();
exit 0;



sub createParentsXML {
	my $st=qq{ select * from SIRtbl where state = '1'};
	my $sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
	$sth->execute() or print "could not execute\n$!";
	my $tmpXml = qq{
<?xml version="1.0" encoding="utf-8"?>
<Events>};
	my $cdmaXml = $tmpXml;
	my $billXml = $tmpXml;
	my $envXml = $tmpXml;
	my $e911Xml = $tmpXml;
	my $transXml = $tmpXml;
	my $dataXml = $tmpXml;
	my $allXml = $tmpXml;
	
	while(my(@result)=$sth->fetchrow_array){
		my $status = "Clear";
		my $meterColor = "0x0174DF";
		my $action = "Activate Event";
		my $color = ""; my $meter = 0;
		my $notes = ""; my $startTime = "";
		my $outageId = "";
		$st=qq{ select * from SIRoutages where sirID = $result[0] and status = '1' order by id desc limit 1};
		my $sth2=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
		$sth2->execute() or print "could not execute\n$!";
		my @result2=$sth2->fetchrow_array;
		if($#result2 <= 0) {
			$st=qq{ select * from SIRinterim where sirID = $result[0] };
			$sth2=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
			$sth2->execute() or print "could not execute\n$!";
			@result2=$sth2->fetchrow_array;
			$notes = $result2[1];
			$meter = $result2[2];
		}
		else {
			$outageId = $result2[0];
			$startTime = $result2[2];
			$notes = $result2[4];
			$meter = $result2[7];
			if($result2[6] == 1) {$status = "Active"; $color="0xFA5858"; $action = "Clear Event"}	
		}
		if($meter <= 25) {$meterColor = "0x0174DF";} #blue
		elsif($meter > 25 && $meter <= 50) {$meterColor = "0xF4FA58";} #yellow
		elsif($meter > 50 && $meter <= 75) {$meterColor = "0xFF9900";} #orange
		elsif($meter > 75) {$meterColor = "0xFA5858";} #red
		
		$tmpXml = qq{
	<event>
		<id>$result[0]</id>
		<section>$result[1]</section>
		<name><![CDATA[$result[3]]]></name>
		<criteria>$result[2]</criteria>
		<status>$status</status>
		<notes>$notes</notes>
		<meter>$meter</meter>
		<metercolor>$meterColor</metercolor>
		<action>$action</action>
		<color>$color</color>
		<outageId>$outageId</outageId>
		<startTime>$startTime</startTime>
	</event>};
		
		if($result[1] eq "CDMA RAN"){$cdmaXml .= $tmpXml;}
		elsif($result[1] eq "BILLING"){$billXml .= $tmpXml;}
		elsif($result[1] eq "ENVIRONMENTAL"){$envXml .= $tmpXml;}
		elsif($result[1] eq "E911"){$e911Xml .= $tmpXml;}
		elsif($result[1] eq "TRANSPORT"){$transXml .= $tmpXml;}
		elsif($result[1] eq "DATA ACCESS"){$dataXml .= $tmpXml;}
		$allXml .= $tmpXml;
	
	}
	$sth->finish;
	$tmpXml = qq{
</Events>};
	$cdmaXml .= $tmpXml;
	$billXml .= $tmpXml;
	$envXml .= $tmpXml;
	$e911Xml .= $tmpXml;
	$transXml .= $tmpXml;
	$dataXml .= $tmpXml;
	$allXml .= $tmpXml;
	open(XML,">/home/weoms/www/apps/SIR/files/cdmaRanEvents.xml");
	print XML $cdmaXml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/billEvents.xml");
	print XML $billXml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/envEvents.xml");
	print XML $envXml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/e911Events.xml");
	print XML $e911Xml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/transEvents.xml");
	print XML $transXml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/dataEvents.xml");
	print XML $dataXml;
	close(XML);
	open(XML,">/home/weoms/www/apps/SIR/files/allEvents.xml");
	print XML $allXml;
	close(XML);


}

