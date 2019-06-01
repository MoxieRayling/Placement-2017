$fn = 50;

difference(){
union(){
cylinder(d=10,6);
translate([-5,0,0])
cube([10,5,6]);
}
translate([-3.1,0.5,-0.05])
cube([6.5,3,6.1]);
translate([0,-2.5,-0.05])
cylinder(d=2.5,6.1);
translate([0,-3,3])
rotate(a=[-90,0,0])
cylinder(d=3,8);
}