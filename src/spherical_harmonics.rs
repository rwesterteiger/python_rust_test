use glam::{Vec3, vec3};
use sphrs::{Coordinates, HarmonicsSet, RealSH, SHEval};

use crate::mesh::{Mesh, Vertex};



pub fn subdiv_rec(m : &mut Mesh, a_idx : u32, b_idx : u32, c_idx : u32, depth : usize) {
  if depth == 0 {
    m.ref_vtx(a_idx);
    m.ref_vtx(b_idx);
    m.ref_vtx(c_idx);
    return
  }

  let pa = m.get(a_idx).pos;
  let pb = m.get(b_idx).pos;
  let pc = m.get(c_idx).pos;

  let ab = (pa + pb).normalize();
  let ab_idx = m.add_vtx(ab, ab);
  
  let bc = (pb + pc).normalize();
  let bc_idx = m.add_vtx(bc, bc);

  let ca = (pc + pa).normalize();
  let ca_idx = m.add_vtx(ca, ca);
  
  let mut rec = |x,y,z| subdiv_rec(m, x,y,z, depth-1);

  rec(a_idx, ab_idx, ca_idx);
  rec(ab_idx, b_idx, bc_idx);
  rec(bc_idx, c_idx, ca_idx);

  rec(ab_idx, bc_idx, ca_idx)
}

pub fn sphere_mesh(depth : usize, radius_func : impl Fn(f32, f32, f32) -> f32) -> Mesh {
  println!("creating sphere mesh");
  
  let mut m = Mesh::new();

  let v = [
    vec3(-1.0,  0.0, 0.0),
    vec3( 0.0, -1.0, 0.0),
    vec3( 1.0,  0.0, 0.0),
    vec3( 0.0,  1.0, 0.0),

    vec3( 0.0,  0.0, 1.0), // idx 4 = north pole
    vec3( 0.0,  0.0,-1.0), // idx 5 = south pole
  ];

  for (idx, p) in v.into_iter().enumerate() {
    let idx2 = m.add_vtx(p, p);
    assert_eq!(idx, idx2 as usize);
  }

  let tris = [
    (0,1,4),
    (1,2,4),
    (2,3,4),
    (3,0,4),
    (1,0,5),
    (2,1,5),
    (3,2,5),
    (0,3,5),
  ];

  for (a,b,c) in tris.into_iter() {
    subdiv_rec(&mut m, a, b, c, depth);
  }

  for p in m.vertices.iter_mut() {
    let r = radius_func(p.pos.x, p.pos.y, p.pos.z);
    p.pos *= r;
  }

  m
}

pub fn sh_mesh(depth : usize) -> Mesh {
  let degree = 1;

  let sh = HarmonicsSet::new(degree, RealSH::Spherical);

  let coeff = vec![1.0; sh.num_sh()];
  let coeff = [0.0, 0.0, 0.0, 1.0];

  println!("{:?}", coeff);

  let radius_func = |x,y,z| {
    let p = Coordinates::cartesian(x, y, z);
    let set = sh.eval_with_coefficients(&p, coeff.as_slice());
    let r : f32 = set.iter().sum();


    r.abs()
  };

  sphere_mesh(depth, radius_func)
}