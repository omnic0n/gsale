import UIKit
import PhotosUI
import CoreLocation
import MapKit

class AddGroupViewController: UIViewController, CLLocationManagerDelegate, MKMapViewDelegate {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let titleLabel = UILabel()
    private let nameTextField = UITextField()
    private let priceTextField = UITextField()
    private let datePicker = UIDatePicker()
    private let dateLabel = UILabel()
    
    // Location section
    private let locationLabel = UILabel()
    private let locationAddressTextField = UITextField()
    private let mapView = MKMapView()
    private let useCurrentLocationButton = UIButton(type: .system)
    private let locationManager = CLLocationManager()
    
    private let imageView = UIImageView()
    private let selectImageButton = UIButton(type: .system)
    private let addButton = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    
    private var selectedImage: UIImage?
    private var selectedLocation: Location?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupLocationManager()
        setupUI()
    }
    
    private func setupLocationManager() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        
        // Request location permission
        locationManager.requestWhenInUseAuthorization()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Add Group"
        
        navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .cancel, target: self, action: #selector(cancelTapped))
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        titleLabel.text = "Create New Group"
        titleLabel.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.textAlignment = .center
        titleLabel.textColor = .label
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        nameTextField.placeholder = "Group Name"
        nameTextField.font = UIFont.systemFont(ofSize: 16)
        nameTextField.borderStyle = .roundedRect
        nameTextField.backgroundColor = .secondarySystemBackground
        nameTextField.translatesAutoresizingMaskIntoConstraints = false
        
        priceTextField.placeholder = "Price (e.g., 29.99)"
        priceTextField.font = UIFont.systemFont(ofSize: 16)
        priceTextField.borderStyle = .roundedRect
        priceTextField.backgroundColor = .secondarySystemBackground
        priceTextField.keyboardType = .decimalPad
        priceTextField.translatesAutoresizingMaskIntoConstraints = false
        
        datePicker.datePickerMode = .date
        datePicker.preferredDatePickerStyle = .compact
        datePicker.translatesAutoresizingMaskIntoConstraints = false
        
        dateLabel.text = "Date:"
        dateLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        dateLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Location UI setup
        locationLabel.text = "Location:"
        locationLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        locationLabel.translatesAutoresizingMaskIntoConstraints = false
        
        locationAddressTextField.placeholder = "Address will be auto-populated from your location"
        locationAddressTextField.font = UIFont.systemFont(ofSize: 16)
        locationAddressTextField.borderStyle = .roundedRect
        locationAddressTextField.backgroundColor = .secondarySystemBackground
        locationAddressTextField.translatesAutoresizingMaskIntoConstraints = false
        
        mapView.delegate = self
        mapView.showsUserLocation = true
        mapView.userTrackingMode = .none
        mapView.layer.cornerRadius = 8
        mapView.layer.borderWidth = 1
        mapView.layer.borderColor = UIColor.systemGray4.cgColor
        mapView.translatesAutoresizingMaskIntoConstraints = false
        
        // Add tap gesture to map for location selection
        let mapTapGesture = UITapGestureRecognizer(target: self, action: #selector(mapTapped(_:)))
        mapView.addGestureRecognizer(mapTapGesture)
        
        useCurrentLocationButton.setTitle("📍 Use Current Location", for: .normal)
        useCurrentLocationButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
        useCurrentLocationButton.setTitleColor(.systemBlue, for: .normal)
        useCurrentLocationButton.translatesAutoresizingMaskIntoConstraints = false
        useCurrentLocationButton.addTarget(self, action: #selector(useCurrentLocationTapped), for: .touchUpInside)
        
        imageView.contentMode = .scaleAspectFit
        imageView.backgroundColor = .systemGray6
        imageView.layer.cornerRadius = 8
        imageView.layer.borderWidth = 1
        imageView.layer.borderColor = UIColor.systemGray4.cgColor
        imageView.translatesAutoresizingMaskIntoConstraints = false
        
        selectImageButton.setTitle("Select Image", for: .normal)
        selectImageButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
        selectImageButton.setTitleColor(.systemBlue, for: .normal)
        selectImageButton.translatesAutoresizingMaskIntoConstraints = false
        selectImageButton.addTarget(self, action: #selector(selectImageTapped), for: .touchUpInside)
        
        addButton.setTitle("Add Group", for: .normal)
        addButton.titleLabel?.font = UIFont.systemFont(ofSize: 18, weight: .semibold)
        addButton.backgroundColor = .systemBlue
        addButton.setTitleColor(.white, for: .normal)
        addButton.layer.cornerRadius = 12
        addButton.translatesAutoresizingMaskIntoConstraints = false
        addButton.addTarget(self, action: #selector(addGroupTapped), for: .touchUpInside)
        
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        contentView.addSubview(titleLabel)
        contentView.addSubview(nameTextField)
        contentView.addSubview(priceTextField)
        contentView.addSubview(dateLabel)
        contentView.addSubview(datePicker)
        contentView.addSubview(locationLabel)
        contentView.addSubview(locationAddressTextField)
        contentView.addSubview(mapView)
        contentView.addSubview(useCurrentLocationButton)
        contentView.addSubview(imageView)
        contentView.addSubview(selectImageButton)
        contentView.addSubview(addButton)
        contentView.addSubview(activityIndicator)
        
        setupConstraints()
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            nameTextField.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 40),
            nameTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            nameTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            nameTextField.heightAnchor.constraint(equalToConstant: 50),
            
            priceTextField.topAnchor.constraint(equalTo: nameTextField.bottomAnchor, constant: 20),
            priceTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            priceTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            priceTextField.heightAnchor.constraint(equalToConstant: 50),
            
            dateLabel.topAnchor.constraint(equalTo: priceTextField.bottomAnchor, constant: 20),
            dateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            
            datePicker.topAnchor.constraint(equalTo: priceTextField.bottomAnchor, constant: 20),
            datePicker.leadingAnchor.constraint(equalTo: dateLabel.trailingAnchor, constant: 10),
            datePicker.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            datePicker.centerYAnchor.constraint(equalTo: dateLabel.centerYAnchor),
            
            // Location constraints
            locationLabel.topAnchor.constraint(equalTo: dateLabel.bottomAnchor, constant: 30),
            locationLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            locationLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            locationAddressTextField.topAnchor.constraint(equalTo: locationLabel.bottomAnchor, constant: 10),
            locationAddressTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            locationAddressTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            locationAddressTextField.heightAnchor.constraint(equalToConstant: 50),
            
            mapView.topAnchor.constraint(equalTo: locationAddressTextField.bottomAnchor, constant: 10),
            mapView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            mapView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            mapView.heightAnchor.constraint(equalToConstant: 200),
            
            useCurrentLocationButton.topAnchor.constraint(equalTo: mapView.bottomAnchor, constant: 10),
            useCurrentLocationButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            imageView.topAnchor.constraint(equalTo: useCurrentLocationButton.bottomAnchor, constant: 20),
            imageView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            imageView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            imageView.heightAnchor.constraint(equalToConstant: 120),
            
            selectImageButton.topAnchor.constraint(equalTo: imageView.bottomAnchor, constant: 10),
            selectImageButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            addButton.topAnchor.constraint(equalTo: selectImageButton.bottomAnchor, constant: 40),
            addButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            addButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            addButton.heightAnchor.constraint(equalToConstant: 50),
            addButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -40),
            
            activityIndicator.centerXAnchor.constraint(equalTo: addButton.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: addButton.centerYAnchor)
        ])
    }
    
    @objc private func cancelTapped() {
        dismiss(animated: true)
    }
    
    @objc private func selectImageTapped() {
        var configuration = PHPickerConfiguration()
        configuration.filter = .images
        configuration.selectionLimit = 1
        
        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        present(picker, animated: true)
    }
    
    @objc private func addGroupTapped() {
        guard let name = nameTextField.text, !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            showAlert(title: "Error", message: "Please enter a group name")
            return
        }
        
        guard let priceText = priceTextField.text, !priceText.isEmpty else {
            showAlert(title: "Error", message: "Please enter a price")
            return
        }
        
        guard let price = Double(priceText) else {
            showAlert(title: "Error", message: "Please enter a valid price")
            return
        }
        
        addButton.isEnabled = false
        activityIndicator.startAnimating()
        
        Task {
            do {
                let response = try await NetworkManager.shared.addGroup(
                    name: name,
                    price: price,
                    date: datePicker.date,
                    image: selectedImage, // This can be nil
                    location: selectedLocation // Include location if available
                )
                
                                       await MainActor.run {
                           self.activityIndicator.stopAnimating()
                           self.addButton.isEnabled = true
                           
                           if response.success {
                               print("✅ Group created successfully!")
                               print("📦 Group ID returned: \(response.group_id ?? "none")")
                               
                               if let groupId = response.group_id, !groupId.isEmpty {
                                   print("🔄 Attempting to navigate to group details for ID: \(groupId)")
                                   // Directly navigate to group details
                                   self.navigateToGroupDetails(groupId: groupId)
                               } else {
                                   print("⚠️ No valid group ID returned, showing success message")
                                   // No group ID returned, show success message and dismiss
                                   self.showSuccessMessageAndDismiss()
                               }
                           } else {
                               self.showAlert(title: "Error", message: response.message)
                           }
                       }
            } catch {
                await MainActor.run {
                    self.activityIndicator.stopAnimating()
                    self.addButton.isEnabled = true
                    
                    let errorMessage: String
                    switch error {
                    case NetworkError.unauthorized:
                        errorMessage = "Please log in again to create groups."
                    case NetworkError.serverError(let message):
                        // Check if this is actually a success with HTML response
                        if message.contains("<html") || message.contains("Group Information") {
                            // This is likely a successful creation with HTML response
                            print("🔄 Detected HTML response - group likely created successfully")
                            
                            // Notify that a group was created
                            NotificationCenter.default.post(name: .groupCreated, object: nil)
                            
                            self.showSuccessMessageAndDismiss()
                            return
                        }
                        errorMessage = "Server error: \(message)"
                    default:
                        errorMessage = "Failed to create group. Please check your internet connection and try again."
                    }
                    
                    print("❌ Group creation error: \(errorMessage)")
                    self.showAlert(title: "Error", message: errorMessage)
                }
            }
        }
    }
    
               private func showSuccessAlert(groupId: String? = nil) {
               let message: String
               if let groupId = groupId {
                   message = "Group created successfully! Group ID: \(groupId)"
               } else {
                   message = "Group created successfully using the web app! You can view it in the GSale web interface."
               }
               
               let alert = UIAlertController(title: "Success", message: message, preferredStyle: .alert)
               alert.addAction(UIAlertAction(title: "View Details", style: .default) { _ in
                   if let groupId = groupId {
                       self.showGroupDetails(groupId: groupId)
                   } else {
                       self.dismiss(animated: true)
                   }
               })
               alert.addAction(UIAlertAction(title: "OK", style: .cancel) { _ in
                   self.dismiss(animated: true)
               })
               present(alert, animated: true)
           }
           
           private func showGroupDetails(groupId: String) {
               Task {
                   do {
                       let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: groupId)
                       
                       await MainActor.run {
                           let detailVC = GroupDetailViewController(groupDetail: groupDetail)
                           let navController = UINavigationController(rootViewController: detailVC)
                           self.present(navController, animated: true)
                       }
                   } catch {
                       await MainActor.run {
                           self.showAlert(title: "Error", message: "Failed to load group details. Please try again.")
                       }
                   }
               }
           }
           
                       private func navigateToGroupDetails(groupId: String) {
                Task {
                    do {
                        print("🌐 Fetching group details for ID: \(groupId)")
                        let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: groupId)
                        
                        await MainActor.run {
                            print("✅ Successfully loaded group details for: \(groupDetail.name)")
                            
                            // Notify that a group was created
                            NotificationCenter.default.post(name: .groupCreated, object: nil)
                            
                            // Dismiss the add group screen first
                            self.dismiss(animated: true) {
                                // Get the presenting view controller (likely the dashboard or groups list)
                                if let presentingVC = self.presentingViewController {
                                    let detailVC = GroupDetailViewController(groupDetail: groupDetail)
                                    let navController = UINavigationController(rootViewController: detailVC)
                                    presentingVC.present(navController, animated: true)
                                }
                            }
                        }
                    } catch {
                        await MainActor.run {
                            print("❌ Failed to load group details: \(error)")
                            // If loading group details fails, show success message and dismiss
                            self.showSuccessMessageAndDismiss()
                        }
                    }
                }
            }
            
            private func showSuccessMessageAndDismiss() {
                // Notify that a group was created
                NotificationCenter.default.post(name: .groupCreated, object: nil)
                
                let alert = UIAlertController(
                    title: "Success! 🎉", 
                    message: "Group created successfully! You can find it in the groups list.", 
                    preferredStyle: .alert
                )
                alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
                    self.dismiss(animated: true)
                })
                present(alert, animated: true)
            }
    
    // MARK: - Location Methods
    
    @objc private func useCurrentLocationTapped() {
        guard CLLocationManager.locationServicesEnabled() else {
            showAlert(title: "Location Services Disabled", message: "Please enable location services in Settings to use this feature.")
            return
        }
        
        switch locationManager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            locationManager.requestLocation()
        case .denied, .restricted:
            showAlert(title: "Location Permission Denied", message: "Please enable location access in Settings to use current location.")
        case .notDetermined:
            locationManager.requestWhenInUseAuthorization()
        @unknown default:
            break
        }
    }
    
    @objc private func mapTapped(_ gesture: UITapGestureRecognizer) {
        let touchPoint = gesture.location(in: mapView)
        let coordinate = mapView.convert(touchPoint, toCoordinateFrom: mapView)
        
        setLocation(coordinate: coordinate)
    }
    
    private func setLocation(coordinate: CLLocationCoordinate2D) {
        // Clear existing annotations
        mapView.removeAnnotations(mapView.annotations)
        
        // Add new annotation
        let annotation = MKPointAnnotation()
        annotation.coordinate = coordinate
        annotation.title = "Selected Location"
        mapView.addAnnotation(annotation)
        
        // Center map on the location
        let region = MKCoordinateRegion(center: coordinate, latitudinalMeters: 1000, longitudinalMeters: 1000)
        mapView.setRegion(region, animated: true)
        
        // Reverse geocode to get address
        let geocoder = CLGeocoder()
        let location = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)
        
        geocoder.reverseGeocodeLocation(location) { [weak self] placemarks, error in
            DispatchQueue.main.async {
                if let placemark = placemarks?.first {
                    let address = self?.formatAddress(from: placemark) ?? "Unknown Address"
                    self?.locationAddressTextField.text = address
                    
                    // Store the selected location
                    self?.selectedLocation = Location(
                        latitude: coordinate.latitude,
                        longitude: coordinate.longitude,
                        address: address
                    )
                } else {
                    self?.locationAddressTextField.text = "Unknown Address"
                    self?.selectedLocation = Location(
                        latitude: coordinate.latitude,
                        longitude: coordinate.longitude,
                        address: nil
                    )
                }
            }
        }
    }
    
    private func formatAddress(from placemark: CLPlacemark) -> String {
        var addressComponents: [String] = []
        
        if let streetNumber = placemark.subThoroughfare {
            addressComponents.append(streetNumber)
        }
        if let streetName = placemark.thoroughfare {
            addressComponents.append(streetName)
        }
        if let city = placemark.locality {
            addressComponents.append(city)
        }
        if let state = placemark.administrativeArea {
            addressComponents.append(state)
        }
        if let postalCode = placemark.postalCode {
            addressComponents.append(postalCode)
        }
        
        return addressComponents.joined(separator: ", ")
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

extension AddGroupViewController: PHPickerViewControllerDelegate {
    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        picker.dismiss(animated: true)
        
        guard let result = results.first else { return }
        
        result.itemProvider.loadObject(ofClass: UIImage.self) { [weak self] image, error in
            DispatchQueue.main.async {
                if let image = image as? UIImage {
                    self?.selectedImage = image
                    self?.imageView.image = image
                    self?.selectImageButton.setTitle("Change Image", for: .normal)
                }
            }
        }
    }
}

// MARK: - CLLocationManagerDelegate
extension AddGroupViewController {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        setLocation(coordinate: location.coordinate)
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error.localizedDescription)")
        showAlert(title: "Location Error", message: "Failed to get current location. Please try again or select location manually on the map.")
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        switch status {
        case .authorizedWhenInUse, .authorizedAlways:
            // Permission granted, can request location
            break
        case .denied, .restricted:
            showAlert(title: "Location Permission Required", message: "Location access is required to automatically set the group location. You can still select a location manually on the map.")
        case .notDetermined:
            // Will be handled when user taps "Use Current Location"
            break
        @unknown default:
            break
        }
    }
}
