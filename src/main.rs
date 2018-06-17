#![allow(warnings)] // remove when error_chain is fixed

//! `cargo run --example simple`

extern crate reqwest;
extern crate env_logger;
#[macro_use]
extern crate error_chain;

use std::fs::File;
use std::io::BufReader;
use std::io::prelude::*;

error_chain! {
    foreign_links {
        ReqError(reqwest::Error);
        IoError(std::io::Error);
    }
}



fn run() -> Result<()> {
    env_logger::init();

    println!("GET https://www.rust-lang.org");

    let mut res = reqwest::get("https://www.rust-lang.org/en-US/")?;

    println!("Status: {}", res.status());
    println!("Headers:\n{}", res.headers());

    // copy the response body directly to stdout
    // let _ = std::io::copy(&mut res, &mut std::io::stdout())?;

    // write the response body to file
    let mut file = File::create("foo.html")?;
    let mut content = res.text()?;
    file.write_all(content.as_bytes()).expect("unable to write data");

    println!("\n\nDone.");
    Ok(())
}

quick_main!(run);