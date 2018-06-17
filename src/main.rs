use std::fs::File;
use std::io::Read;
use std::io::prelude::*;

fn main() {
    // println!("Hello, world!");

    let mut resp = reqwest::get("http://showrss.info/597.rss")?;
    assert!(resp.status().is_success());

    let mut content = String::new();
    resp.read_to_string(&mut content);

    let mut file = File::create("../../..feeds/597.rss")?;
    file.write_all(content)?;

    OK(())
}
