use std::env;
use std::net::SocketAddr;
use std::time::SystemTime;

use rocket::request::{FromRequest, Outcome};
use rocket::serde::json::Json;
use rocket::{post, Request}; use rocket::{
    get,
    http::Status,
    launch, put,
    response::{status, Redirect},
    routes,
};
use serde_json::json;
use track::{random_id, save, Click, Coordinates, Service, Tracker};
use user_agent_parser::{Device, Engine, Product, UserAgent, UserAgentParser, CPU, OS};


mod track;

struct ApiKey(String);

#[rocket::async_trait]
impl<'r> FromRequest<'r> for ApiKey {
    type Error = ();

    async fn from_request(req: &'r Request<'_>) -> Outcome<Self, Self::Error> {
        // Get API Key from environment variable
        let expected_key = match env::var("TRACKER_ADMIN_KEY") {
            Ok(key) => key,
            Err(_) => {
                eprintln!("TRACKER_ADMIN_KEY environment variable not set");
                return Outcome::Error((Status::InternalServerError, ()));
            }
        };

        // Extract API key from header
        match req.headers().get_one("X-API-Key") {
            Some(received_key) if received_key == expected_key => Outcome::Success(ApiKey(received_key.to_string())),
            _ => Outcome::Error((Status::Unauthorized, ())),
        }
    }
}

#[put("/new_track?<campaign>", data = "<url>")]
fn new_track(campaign : &str, url: &str, _api_key: ApiKey) -> Result<String, status::Custom<String>> {
    let service_opt = track::load();

    let mut service = service_opt.unwrap_or_default();

    let id = random_id();
    let tracker = Tracker {
            campaign: campaign.to_string(),
            loc: None,
            id: id.clone(),
            log: vec![],
            url: url.to_string(),
    };
    service.trackers.insert(
        id.clone(),
        tracker.clone(),
    );
    let _ = track::save(&service).map_err(|_| status::Custom(Status::InternalServerError, json!({"error":"Could not save track to database"})));
    
    return Ok(json!({"success": true, "tracker" : tracker}).to_string());
}

#[get("/get_track/<id>")]
fn get_track(id: &str, _api_key: ApiKey) -> Result<Json<String>, status::Custom<String>> {
    let service_opt = track::load();

    let mut service = match service_opt {
        Some(a) => a,
        None => Service::default(),
    };

    let tracker = service.trackers.get_mut(id);

    match tracker {
        Some(t) => serde_json::to_string(t).map(Json).map_err(|_| {
            status::Custom(
                Status::InternalServerError,
                "Serialization error".to_string(),
            )
        }),
        None => Err(status::Custom(
            Status::NotFound,
            json!({"error": "Tracker does not exist"}).to_string(),
        )),
    }
}

#[post("/geotag/<id>?<lon>&<lat>")]
fn geotag(id: &str, lon: f32, lat: f32, _api_key: ApiKey) -> Result<(), status::Custom<String>> {
    let service_opt = track::load();

    let mut service = match service_opt {
        Some(a) => a,
        None => Service::default(),
    };

    let tracker = service.trackers.get_mut(id);

    match tracker {
        Some(t) => {
            let lat_micro = (lat * 1_000_000.0).round() as i32;
            let lon_micro = (lon * 1_000_000.0).round() as i32;

            t.loc = Some(Coordinates {
                lat: lat_micro,
                lon: lon_micro,
            });

            let _ = track::save(&service).map_err(|_| status::Custom(Status::InternalServerError, json!({"error":"Could not save track to database"})));
            return Ok(())
        },
        None => Err(status::Custom(
            Status::NotFound,
            json!({"error": "Tracker does not exist"}).to_string(),
        )),
    }

}

#[get("/get_all_tracks")]
fn get_all_tracks(_api_key: ApiKey) -> Result<Json<String>, status::Custom<String>> {
    let service_opt = track::load();

    let service = match service_opt {
        Some(a) => a,
        None => Service::default(),
    };

    return serde_json::to_string(&service).map(Json).map_err(|_| {
        status::Custom(
            Status::InternalServerError,
            "Serialization error".to_string(),
        )
    });
}

#[get("/<id>")]
fn redirect_request(
    id: &str,
    remote_addr: SocketAddr,
    user_agent: UserAgent,
    product: Product,
    os: OS,
    device: Device,
    cpu: CPU,
    engine: Engine,
) -> Result<Redirect, status::Custom<String>> {
    let service_opt = track::load();

    let mut service = service_opt.unwrap_or_default();

    let tracker_opt = service.trackers.get_mut(id);

    match tracker_opt {
        Some(tracker) => {
            let click = Click {
                time: SystemTime::now(),
                ip: remote_addr.ip(),
                user_agent: user_agent
                    .user_agent
                    .ok_or("No user agent")
                    .unwrap_or(std::borrow::Cow::Owned(
                        "Could not unwrap user agent".to_string(),
                    ))
                    .to_string(),
                success: true,
                product: format!(
                    "{}",
                    product
                        .name
                        .unwrap_or(std::borrow::Cow::Owned("Unknown Product".to_string()))
                        .to_string()
                ),
                os: format!(
                    "{}",
                    os.name
                        .unwrap_or(std::borrow::Cow::Owned(
                            "Unknown Operating System".to_string()
                        ))
                        .to_string()
                ),
                device: format!(
                    "{}",
                    device
                        .name
                        .unwrap_or(std::borrow::Cow::Owned("Unknown Device".to_string()))
                        .to_string()
                ),
                cpu: format!(
                    "{}",
                    cpu.architecture
                        .unwrap_or(std::borrow::Cow::Owned(
                            "Unknown CPU Archtecture".to_string()
                        ))
                        .to_string()
                ),
                engine: format!(
                    "{}",
                    engine
                        .name
                        .unwrap_or(std::borrow::Cow::Owned(
                            "Unknown CPU Archtecture".to_string()
                        ))
                        .to_string()
                ),
            };
            tracker.log.push(click);
            let redirect = Redirect::to(tracker.url.clone());
            let _ = save(&service);
            Ok(redirect)
        }
        None => Err(status::Custom(
            Status::NotFound,
            json!({"error": "Tracker does not exist"}).to_string(),
        )),
    }
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .manage(UserAgentParser::from_str(include_str!("./user_agents.yaml")).unwrap())
        .mount("/track", routes![get_track, new_track, get_all_tracks, geotag])
        .mount("/", routes![redirect_request])
}
