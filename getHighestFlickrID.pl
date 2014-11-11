# Attempt to find highest flickr id using binary search
# A single search fails because there are holes in the ranges of valid photo ids
# but a good lower bound can be found by doing multiple searches, resetting the upper bound to LB*3 each time,
# until stability is reached.
#
# 3-25-2013: 8,590,506,818

use Flickr::API;
use XML::Simple;
use Data::Dumper;

$| = 1;

$Data::Dumper::Terse = 1;  # avoids $VAR1 = * ; in dumper output
$Data::Dumper::Indent = $verbose? 1 : 0;  # more concise output

require 'apikey.ph';

my $api = new Flickr::API({'key' => $api_key, secret => $sharedsecret});
$xmlp = new XML::Simple ();


my $maxID = 1000000000000; # one trillion
my $minID = 10000; # ten thousand
my $method = 'flickr.photos.getInfo';

# binary search for highest flickr id
my $lastReset = 0;

while ($maxID > $minID+1) {
  my $medID = int(($maxID+$minID)/2);
  print "Testing medID: " . $medID . "\n";
  my $response = $api->execute_method('flickr.photos.getInfo', {
                    photo_id => $medID} );
  my $xml = $response->decoded_content;
  my $xm = $xmlp->XMLin($xml,forcearray=>['photo']);

  # print Dumper($response);  # explore results of call using -verbose
  if ($xm->{stat} eq 'fail' and $xm->{err}->{msg} =~ m/\bnot found\b/)
  {
    $maxID = $medID;
    print "  <\n";
  } else {
    print "  >\n";
    $minID = $medID;
#    print "\n\n";
#    print Dumper($xm);
#    exit;
  }
  if ($maxID < $minID+2) {
    if ($minID == $lastReset) {
      last;
    }
    $lastReset = $minID;
    print "Reset at $minID\n";
    $maxID = $minID * 3;
  }
  # exit;
}
print "Final: $minID\n";



