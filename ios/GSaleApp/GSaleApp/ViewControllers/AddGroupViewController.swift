import UIKit
import PhotosUI
import CoreLocation
import MapKit
import AVFoundation

class AddGroupViewController: UIViewController, CLLocationManagerDelegate, MKMapViewDelegate, UITextFieldDelegate, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    
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
        setupKeyboardDismissal()
    }
    
    private func setupKeyboardDismissal() {
        // Add tap gesture to dismiss keyboard when tapping outside text fields
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        tapGesture.cancelsTouchesInView = false
        view.addGestureRecognizer(tapGesture)
        
        // Set up text field delegates for return key handling
        nameTextField.delegate = self
        priceTextField.delegate = self
        locationAddressTextField.delegate = self
        
        // Set up keyboard notifications
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillShow),
            name: UIResponder.keyboardWillShowNotification,
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillHide),
            name: UIResponder.keyboardWillHideNotification,
            object: nil
        )
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func keyboardWillShow(_ notification: Notification) {
        guard let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect else { return }
        guard let animationDuration = notification.userInfo?[UIResponder.keyboardAnimationDurationUserInfoKey] as? Double else { return }
        
        let keyboardHeight = keyboardFrame.height
        let contentInsets = UIEdgeInsets(top: 0, left: 0, bottom: keyboardHeight, right: 0)
        
        UIView.animate(withDuration: animationDuration) {
            self.scrollView.contentInset = contentInsets
            self.scrollView.scrollIndicatorInsets = contentInsets
        }
    }
    
    @objc private func keyboardWillHide(_ notification: Notification) {
        guard let animationDuration = notification.userInfo?[UIResponder.keyboardAnimationDurationUserInfoKey] as? Double else { return }
        
        UIView.animate(withDuration: animationDuration) {
            self.scrollView.contentInset = .zero
            self.scrollView.scrollIndicatorInsets = .zero
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    private func setupLocationManager() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        
        // Request location permission and automatically get current location
        locationManager.requestWhenInUseAuthorization()
        
        // Automatically request current location if we have permission
        if CLLocationManager.locationServicesEnabled() {
            switch locationManager.authorizationStatus {
            case .authorizedWhenInUse, .authorizedAlways:
                requestCurrentLocation()
            case .notDetermined:
                // Will be handled in didChangeAuthorization delegate method
                break
            default:
                // Set placeholder text to indicate location is optional
                locationAddressTextField.placeholder = "Location (optional) - tap 'Use Current Location' or select on map"
            }
        }
    }
    
    private func requestCurrentLocation() {
        locationAddressTextField.placeholder = "Getting current location..."
        useCurrentLocationButton.setTitle("📍 Getting Location...", for: .normal)
        useCurrentLocationButton.isEnabled = false
        
        locationManager.requestLocation()
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
        
        locationAddressTextField.placeholder = "Detecting current location..."
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
        let alertController = UIAlertController(title: "Select Image", message: "Choose how you'd like to add an image", preferredStyle: .actionSheet)
        
        // Camera option
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            let cameraAction = UIAlertAction(title: "📷 Take Photo", style: .default) { _ in
                self.checkCameraPermissionAndPresent()
            }
            alertController.addAction(cameraAction)
        }
        
        // Photo Library option
        let libraryAction = UIAlertAction(title: "📱 Choose from Library", style: .default) { _ in
            self.presentPhotoLibrary()
        }
        alertController.addAction(libraryAction)
        
        // Cancel option
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel)
        alertController.addAction(cancelAction)
        
        // For iPad support
        if let popover = alertController.popoverPresentationController {
            popover.sourceView = selectImageButton
            popover.sourceRect = selectImageButton.bounds
        }
        
        present(alertController, animated: true)
    }
    
    private func checkCameraPermissionAndPresent() {
        let cameraAuthorizationStatus = AVCaptureDevice.authorizationStatus(for: .video)
        
        switch cameraAuthorizationStatus {
        case .authorized:
            presentCamera()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async {
                    if granted {
                        self.presentCamera()
                    } else {
                        self.showCameraPermissionDeniedAlert()
                    }
                }
            }
        case .denied, .restricted:
            showCameraPermissionDeniedAlert()
        @unknown default:
            showCameraPermissionDeniedAlert()
        }
    }
    
    private func presentCamera() {
        let imagePickerController = UIImagePickerController()
        imagePickerController.sourceType = .camera
        imagePickerController.mediaTypes = ["public.image"]
        imagePickerController.allowsEditing = true
        imagePickerController.delegate = self
        present(imagePickerController, animated: true)
    }
    
    private func presentPhotoLibrary() {
        var configuration = PHPickerConfiguration()
        configuration.filter = .images
        configuration.selectionLimit = 1
        
        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        present(picker, animated: true)
    }
    
    private func showCameraPermissionDeniedAlert() {
        let alert = UIAlertController(
            title: "Camera Access Required",
            message: "Please enable camera access in Settings to take photos for your groups.",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "Settings", style: .default) { _ in
            if let settingsURL = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(settingsURL)
            }
        })
        
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        present(alert, animated: true)
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
                                   print("⚠️ No valid group ID returned, dismissing without popup")
                                   // No group ID returned, just dismiss and notify groups list to refresh
                                   NotificationCenter.default.post(name: .groupCreated, object: nil)
                                   self.dismiss(animated: true)
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
                            
                            // Notify that a group was created and dismiss
                            NotificationCenter.default.post(name: .groupCreated, object: nil)
                            self.dismiss(animated: true)
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
                            // If loading group details fails, just dismiss without popup
                            NotificationCenter.default.post(name: .groupCreated, object: nil)
                            self.dismiss(animated: true)
                        }
                    }
                }
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
                    self?.locationAddressTextField.placeholder = "Tap to edit address"
                    
                    // Store the selected location
                    self?.selectedLocation = Location(
                        latitude: coordinate.latitude,
                        longitude: coordinate.longitude,
                        address: address
                    )
                    
                    print("📍 Location set: \(address)")
                    print("📍 Coordinates: \(coordinate.latitude), \(coordinate.longitude)")
                } else {
                    let coordinateString = String(format: "%.6f, %.6f", coordinate.latitude, coordinate.longitude)
                    self?.locationAddressTextField.text = coordinateString
                    self?.locationAddressTextField.placeholder = "Address not found - coordinates used"
                    self?.selectedLocation = Location(
                        latitude: coordinate.latitude,
                        longitude: coordinate.longitude,
                        address: nil
                    )
                    
                    print("📍 Location set with coordinates only: \(coordinateString)")
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

// MARK: - UIImagePickerControllerDelegate
extension AddGroupViewController {
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        picker.dismiss(animated: true)
        
        // Try to get the edited image first, then the original
        var selectedImage: UIImage?
        if let editedImage = info[.editedImage] as? UIImage {
            selectedImage = editedImage
        } else if let originalImage = info[.originalImage] as? UIImage {
            selectedImage = originalImage
        }
        
        if let image = selectedImage {
            self.selectedImage = image
            self.imageView.image = image
            self.selectImageButton.setTitle("Change Image", for: .normal)
        }
    }
    
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true)
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
        
        // Reset button state
        useCurrentLocationButton.setTitle("📍 Use Current Location", for: .normal)
        useCurrentLocationButton.isEnabled = true
        
        setLocation(coordinate: location.coordinate)
    }
    
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error.localizedDescription)")
        
        // Reset button state
        useCurrentLocationButton.setTitle("📍 Use Current Location", for: .normal)
        useCurrentLocationButton.isEnabled = true
        locationAddressTextField.placeholder = "Location (optional) - tap 'Use Current Location' or select on map"
        
        showAlert(title: "Location Error", message: "Failed to get current location. Please try again or select location manually on the map.")
    }
    
    func locationManager(_ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus) {
        switch status {
        case .authorizedWhenInUse, .authorizedAlways:
            // Permission granted, automatically request current location
            requestCurrentLocation()
        case .denied, .restricted:
            locationAddressTextField.placeholder = "Location (optional) - select on map or enter manually"
            useCurrentLocationButton.setTitle("📍 Use Current Location", for: .normal)
            useCurrentLocationButton.isEnabled = true
            showAlert(title: "Location Permission Required", message: "Location access is required to automatically set the group location. You can still select a location manually on the map.")
        case .notDetermined:
            // Will be handled when user taps "Use Current Location"
            break
        @unknown default:
            locationAddressTextField.placeholder = "Location (optional) - select on map or enter manually"
            useCurrentLocationButton.setTitle("📍 Use Current Location", for: .normal)
            useCurrentLocationButton.isEnabled = true
            break
        }
    }
    // MARK: - UITextFieldDelegate
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        if textField == nameTextField {
            priceTextField.becomeFirstResponder()
        } else if textField == priceTextField {
            locationAddressTextField.becomeFirstResponder()
        } else if textField == locationAddressTextField {
            textField.resignFirstResponder()
        } else {
            textField.resignFirstResponder()
        }
        return true
    }
    
    func textFieldDidBeginEditing(_ textField: UITextField) {
        // Scroll to the text field when it becomes active to ensure it's visible
        let textFieldFrame = view.convert(textField.frame, from: textField.superview)
        let visibleRect = CGRect(x: 0, y: textFieldFrame.origin.y - 50, width: scrollView.frame.width, height: textFieldFrame.height + 100)
        scrollView.scrollRectToVisible(visibleRect, animated: true)
    }
}
