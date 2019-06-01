#! /usr/bin/perl -w
# program accepts 4 arguments, in the form stepper.pl  Motor1Dir, Motor2Dir, Wait, Steps
# e.g.
#   perl  stepper.pl -1 1 2 1000
# directions of motors  1=clockwise 0=not moving -1=anticlockwise
# (twice because of 2 motors)
# wait in number of milliseconds between each 4-step step
# number of steps toi be taken

use Device::I2C;                     # allows I2C comms in
use Time::HiRes ('sleep');           # allows waits less than 1 second
use Fcntl;                           # includes definitions e.g. O_RDWR
   $dev = Device::I2C->new('/dev/i2c-1', O_RDWR);   #Create a new device
   $dev->selectDevice(0x24);
   $dev->writeByteData(0x00,0x00);
   @steps=(0x03,0x06,0x0c,0x09);     #clockwise nibbles

# next 4 lines check for 4 arguments
   $num_args = $#ARGV + 1;
   if ($num_args != 4) {
    print "
Usage:      testi2c.pl  Motor1Dir, Motor2Dir, Wait, Steps
Directions: 1=clockwise, 0 not moving, -1=antictockwise
Wait:       milliseconds; times <2ms do not work
Steps:      integer number of steps\n\n";
    exit;
   }

   stepper(@ARGV);    #call function
 sub stepper{
   my ($m1dir,$m2dir,$wait,$steps)=@_;
   $wait=$wait/1000;
   my $a=(($m1dir==1)?$steps[0]:(($m1dir==-1)?$steps[3]:0))+
         (($m2dir==1)?$steps[0]*0x10:(($m1dir==-1)?$steps[3]*0x10:0));
   my $b=(($m1dir==1)?$steps[1]:(($m1dir==-1)?$steps[2]:0))+
         (($m2dir==1)?$steps[1]*0x10:(($m1dir==-1)?$steps[2]*0x10:0));
   my $c=(($m1dir==1)?$steps[2]:(($m1dir==-1)?$steps[1]:0))+
         (($m2dir==1)?$steps[2]*0x10:(($m1dir==-1)?$steps[1]*0x10:0));
   my $d=(($m1dir==1)?$steps[3]:(($m1dir==-1)?$steps[0]:0))+
         (($m2dir==1)?$steps[3]*0x10:(($m1dir==-1)?$steps[0]*0x10:0));

  for (my $x=0;$x<$steps;$x++){
   $dev->writeByteData(0x14,$a);
   sleep($wait);
   $dev->writeByteData(0x14,$b);
   sleep($wait);
   $dev->writeByteData(0x14,$c);
   sleep($wait);
   $dev->writeByteData(0x14,$d);
   sleep($wait);
  }
   # at the end of functions sets all outputs to 0 to save power
   $dev->writeByteData(0x14,0x00);
}

exit 1;



