import Foundation
import CoreLocation

struct Venue: Identifiable, Codable, Hashable {
    let id: Int
    let name: String
    let category: String
    let address: String
    let latitude: Double
    let longitude: Double
    let description: String?

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }

    func distance(from location: CLLocationCoordinate2D) -> Double {
        let venueLocation = CLLocation(latitude: latitude, longitude: longitude)
        let userLocation = CLLocation(latitude: location.latitude, longitude: location.longitude)
        return userLocation.distance(from: venueLocation) / 1000.0 // Convert to km
    }
}
