#!/usr/local/bin/perl

use Flickr::API;
use XML::Simple;
use Data::Dumper;
use Math::Random::MT::Perl qw(srand rand);

$| = 1;

$Data::Dumper::Terse = 1;  # avoids $VAR1 = * ; in dumper output
$Data::Dumper::Indent = $verbose? 1 : 0;  # more concise output

require 'apikey.ph';  # contains $api_key and $sharedsecret

my $api = new Flickr::API({'key' => $api_key, secret => $sharedsecret});
$xmlp = new XML::Simple ();


my $maxID = 8590506818;

my @knownPhotos = ();
my %knownIDs = ();
# collect known photos
for $file (<cache/*.jpg>) {
  my ($id) = $file =~ m~\b(\d+)_\w+.jpg~;
  printf "%s\n", $id;
  $knownIDs{$id} = 1;
  push @knownPhotos, $file;
}

sub MakeFlickrPath($$)
{
  my ($photo, $suffix) = @_;
  return sprintf "http://farm%s.static.flickr.com/%d/%s_%s%s.jpg", 
              $photo->{farm},
        $photo->{server},
        $photo->{id}, 
        $photo->{secret}, $suffix;
}
sub MakeFilename($$)
{
  my ($photo, $suffix) = @_;
  return sprintf "%s_%s%s.jpg", 
        $photo->{id}, 
        $photo->{secret}, $suffix;
}

while (scalar(@knownPhotos) < 10000) {
  my $id = int(rand()*$maxID);
  next if defined $knownIDs{$id};
  print "Testing $id\n";
  my $response = $api->execute_method('flickr.photos.getInfo', {
                    photo_id => $id} );
  my $xml = $response->decoded_content;
  my $xm = $xmlp->XMLin($xml,forcearray=>['id']);
  if ($xm->{stat} ne 'fail') {
    print "Success - downloading image\n";
    my $url = MakeFlickrPath($xm->{photo}, '');
    my $filename = MakeFilename($xm->{photo}, '');
    my $cmd = sprintf 'curl "%s" >cache/%s', $url, $filename;
    printf "%s\n", $url;
    system($cmd);
    # exit;
    push @knownPhotos, $filename;
    $knownIDs{$id} = 1;
  }
}
