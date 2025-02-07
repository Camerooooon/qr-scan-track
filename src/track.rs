use std::{
    collections::HashMap, env, fs::{self, File}, io::{Read, Write}, net::IpAddr, time::SystemTime
};

extern crate alloc;

use random_string::generate;
use rocket::serde::{Deserialize, Serialize};

use alloc::vec::Vec;
use serde_json::to_string;

const ID_CHARSET: &str = "abcdef1234567890";

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq, Clone)]
#[serde(crate = "rocket::serde")]
pub struct Click {
    pub time: SystemTime,
    pub ip: IpAddr,
    pub success: bool,
    pub user_agent: String,
    pub product: String,
    pub os: String,
    pub device: String,
    pub cpu: String,
    pub engine: String,
}

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq, Clone)]
#[serde(crate = "rocket::serde")]
pub struct Coordinates {
    pub lon: i32,
    pub lat: i32,
}

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq, Clone)]
#[serde(crate = "rocket::serde")]
pub struct Tracker {
    pub campaign: String,
    pub log: Vec<Click>,
    pub loc: Option<Coordinates>,
    pub url: String,
    pub id: String,
}

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq)]
#[serde(crate = "rocket::serde")]
pub struct Service {
    pub trackers: HashMap<String, Tracker>,
}

pub fn random_id() -> String {
    return generate(5, ID_CHARSET);
}

pub fn load() -> Option<Service> {
    let db_path = env::var("TRACKER_DATABASE_PATH").expect("TRACKER_DATABASE_PATH not set");
    let file_opt = File::open(&db_path);

    let mut file = match file_opt {
        Ok(a) => a,
        Err(e) => {
            println!("Failed to open file: {}", e);
            return None;
        }
    };

    let mut buffer = String::new();
    file.read_to_string(&mut buffer)
        .expect("Could not read buffer");
    let service: Result<Service, serde_json::Error> = serde_json::from_str(buffer.as_str());

    match service {
        Ok(s) => Some(s),
        Err(e) => {
            println!("Could not deserilize service file: {}", e);
            None
        }
    }
}

pub fn save(service: &Service) -> Result<(), std::io::Error> {
    let bytes: String = to_string(service).expect("Could not serialize tracker");

    let db_path = env::var("TRACKER_DATABASE_PATH").expect("TRACKER_DATABASE_PATH not set");
    let mut file = fs::OpenOptions::new()
        .create(true)
        .write(true)
        .open(db_path)?;

    file.write_all(&bytes.as_bytes())
}

impl Default for Service {
    fn default() -> Service {
        Service {
            trackers: HashMap::new(),
        }
    }
}
