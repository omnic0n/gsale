import UIKit
import PhotosUI

class AddGroupViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let titleLabel = UILabel()
    private let nameTextField = UITextField()
    private let priceTextField = UITextField()
    private let datePicker = UIDatePicker()
    private let dateLabel = UILabel()
    private let imageView = UIImageView()
    private let selectImageButton = UIButton(type: .system)
    private let addButton = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    
    private var selectedImage: UIImage?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
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
            
            imageView.topAnchor.constraint(equalTo: dateLabel.bottomAnchor, constant: 20),
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
                    image: selectedImage // This can be nil
                )
                
                                       await MainActor.run {
                           self.activityIndicator.stopAnimating()
                           self.addButton.isEnabled = true
                           
                           if response.success {
                               self.showSuccessAlert(groupId: response.group_id)
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
                        errorMessage = "Server error: \(message)"
                    default:
                        errorMessage = "Failed to create group. Please check your internet connection and try again."
                    }
                    
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
