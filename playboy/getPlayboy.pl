#!/usr/local/bin/perl -s

# Script to retrieve playboy images from imgur (using info in captured JSON data)

# Code used to make the images in http://krazydad.com/blog/2016/03/02/emergent-orange-and-playboy-centerfolds/

# Note: I ended up manually cropping the following 3 images before making my Amalgams: 
#   1954_11, 1956_02, 1958_10

use Data::Dumper;
use lib qw(..);
use JSON qw( );

$| = 1;
$Data::Dumper::Terse = 1;  # avoids $VAR1 = * ; in dumper output
$Data::Dumper::Indent = $verbose? 1 : 0;  # more concise output

my $filename = 'playboy.json';
my $json_text = do {
   open(my $json_fh, "<:encoding(UTF-8)", $filename)
      or die("Can't open \$filename\": $!\n");
   local $/;
   <$json_fh>
};
my $json = JSON->new;
my $data = $json->decode($json_text);

for ( @{$data->{data}} ) {
   print $_->{name}."\n";
}


my $pfiles = $data->{album_images}->{images};

printf "Got %d files\n", $pfiles;
%mon_nums = ('january' => 1, 'february' => 2, 'march' => 3, 'april' => 4, 'may' => 5, 'june' => 6, 
             'july' => 7, 'august' => 8, 'september' => 9, 'october' => 10, 'november' => 11, 'december' => 12);

for my $file (@$pfiles) {
  $title = $file->{title};
  if ($title =~ /(\w+) ((19|20)\d\d)/) {
      ($mon,$year) = (lc($1),$2);
      # print "$mon $year\n";
      if (defined $mon_nums{$mon}) {
        $mon_num = $mon_nums{$mon};
        $decade = $year - ($year % 10);
        if (not -e "./$decade") {
          `mkdir $decade`;
        }
        $url = 'http://i.imgur.com/' . $file->{hash} . '.jpg';
        $lfile = sprintf './%s/%04d_%02d.jpg', $decade, $year, $mon_num;
        if (not -e $lfile) {
            print $lfile . "\n";
            $cmd = "curl '$url' >'$lfile'";
            print "$cmd\n";
            `$cmd`;
        }
     }
  }
}



