import UIKit

class ModifyGroupViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let nameTextField = UITextField()
    private let priceTextField = UITextField()
    private let dateTextField = UITextField()
    private let saveButton = UIButton(type: .system)
    private let imagePreview = UIImageView()
    private let changeImageButton = UIButton(type: .system)
    private var selectedImage: UIImage?
    
    private let nameLabel = UILabel()
    private let priceLabel = UILabel()
    private let dateLabel = UILabel()
    
    private let groupId: String
    private let groupName: String
    
    init(groupId: String, groupName: String) {
        self.groupId = groupId
        self.groupName = groupName
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupData()
        setupKeyboardDismissal()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Modify Group"
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        // Name field setup
        nameLabel.text = "Group Name"
        nameLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        nameLabel.textColor = .label
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        
        nameTextField.borderStyle = .roundedRect
        nameTextField.font = UIFont.systemFont(ofSize: 16)
        nameTextField.translatesAutoresizingMaskIntoConstraints = false
        
        // Price field setup
        priceLabel.text = "Price"
        priceLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        priceLabel.textColor = .label
        priceLabel.translatesAutoresizingMaskIntoConstraints = false
        
        priceTextField.borderStyle = .roundedRect
        priceTextField.font = UIFont.systemFont(ofSize: 16)
        priceTextField.keyboardType = .decimalPad
        priceTextField.translatesAutoresizingMaskIntoConstraints = false
        
        // Date field setup
        dateLabel.text = "Date"
        dateLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        dateLabel.textColor = .label
        dateLabel.translatesAutoresizingMaskIntoConstraints = false
        
        dateTextField.borderStyle = .roundedRect
        dateTextField.font = UIFont.systemFont(ofSize: 16)
        dateTextField.translatesAutoresizingMaskIntoConstraints = false
        
        // Image preview
        imagePreview.translatesAutoresizingMaskIntoConstraints = false
        imagePreview.contentMode = .scaleAspectFill
        imagePreview.layer.cornerRadius = 8
        imagePreview.layer.masksToBounds = true
        imagePreview.backgroundColor = .systemGray6

        changeImageButton.setTitle("Change Image", for: .normal)
        changeImageButton.backgroundColor = .systemGray
        changeImageButton.setTitleColor(.white, for: .normal)
        changeImageButton.layer.cornerRadius = 8
        changeImageButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        changeImageButton.translatesAutoresizingMaskIntoConstraints = false
        changeImageButton.addTarget(self, action: #selector(changeImageTapped), for: .touchUpInside)

        // Save button setup
        saveButton.setTitle("Save Changes", for: .normal)
        saveButton.backgroundColor = .systemBlue
        saveButton.setTitleColor(.white, for: .normal)
        saveButton.layer.cornerRadius = 8
        saveButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        saveButton.translatesAutoresizingMaskIntoConstraints = false
        saveButton.addTarget(self, action: #selector(saveButtonTapped), for: .touchUpInside)
        
        // Add subviews
        contentView.addSubview(nameLabel)
        contentView.addSubview(nameTextField)
        contentView.addSubview(priceLabel)
        contentView.addSubview(priceTextField)
        contentView.addSubview(dateLabel)
        contentView.addSubview(dateTextField)
        contentView.addSubview(imagePreview)
        contentView.addSubview(changeImageButton)
        contentView.addSubview(saveButton)
        
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
            
            nameLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 30),
            nameLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            nameLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            nameTextField.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 8),
            nameTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            nameTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            nameTextField.heightAnchor.constraint(equalToConstant: 44),
            
            priceLabel.topAnchor.constraint(equalTo: nameTextField.bottomAnchor, constant: 20),
            priceLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            priceLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            priceTextField.topAnchor.constraint(equalTo: priceLabel.bottomAnchor, constant: 8),
            priceTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            priceTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            priceTextField.heightAnchor.constraint(equalToConstant: 44),
            
            dateLabel.topAnchor.constraint(equalTo: priceTextField.bottomAnchor, constant: 20),
            dateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            dateLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            dateTextField.topAnchor.constraint(equalTo: dateLabel.bottomAnchor, constant: 8),
            dateTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            dateTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            dateTextField.heightAnchor.constraint(equalToConstant: 44),

            imagePreview.topAnchor.constraint(equalTo: dateTextField.bottomAnchor, constant: 20),
            imagePreview.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            imagePreview.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            imagePreview.heightAnchor.constraint(equalToConstant: 180),

            changeImageButton.topAnchor.constraint(equalTo: imagePreview.bottomAnchor, constant: 12),
            changeImageButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            changeImageButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            changeImageButton.heightAnchor.constraint(equalToConstant: 44),
            
            saveButton.topAnchor.constraint(equalTo: changeImageButton.bottomAnchor, constant: 24),
            saveButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            saveButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            saveButton.heightAnchor.constraint(equalToConstant: 50),
            saveButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -30)
        ])
    }
    
    private func setupData() {
        nameTextField.text = groupName
        priceTextField.text = "0.00"
        dateTextField.text = "2025-07-30"
        
        // Fetch actual group data from backend
        Task {
            await loadGroupData()
        }
    }
    
    private func loadGroupData() async {
        do {
            let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: groupId)
            
            DispatchQueue.main.async {
                self.nameTextField.text = groupDetail.name
                self.priceTextField.text = String(format: "%.2f", groupDetail.price)
                self.dateTextField.text = groupDetail.date
                if let imageFilename = groupDetail.imageFilename, !imageFilename.isEmpty {
                    let urlString = "https://gsale.levimylesllc.com/static/uploads/\(imageFilename)"
                    if let url = URL(string: urlString) {
                        Task {
                            if let (data, response) = try? await URLSession.shared.data(from: url),
                               let http = response as? HTTPURLResponse, http.statusCode == 200,
                               let img = UIImage(data: data) {
                                await MainActor.run { self.imagePreview.image = img }
                            }
                        }
                    }
                }
            }
        } catch {
            // Keep the default values if loading fails
        }
    }
    
    @objc private func saveButtonTapped() {
        guard let name = nameTextField.text, !name.isEmpty,
              let priceText = priceTextField.text, let price = Double(priceText),
              let date = dateTextField.text, !date.isEmpty else {
            showAlert(title: "Error", message: "Please fill in all fields correctly")
            return
        }
        
        // Show loading indicator
        let loadingAlert = UIAlertController(title: "Saving...", message: nil, preferredStyle: .alert)
        present(loadingAlert, animated: true)
        
        Task {
            do {
                // Call the modify group API
                try await NetworkManager.shared.modifyGroup(groupId: groupId, name: name, price: price, date: date, image: self.selectedImage)
                
                let updatedDetail = try await NetworkManager.shared.getGroupDetails(groupId: self.groupId)
                DispatchQueue.main.async {
                    loadingAlert.dismiss(animated: true) {
                        // Pop back and broadcast refresh
                        NotificationCenter.default.post(name: .groupUpdated, object: updatedDetail)
                        self.navigationController?.popViewController(animated: true)
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    loadingAlert.dismiss(animated: true) {
                        self.showAlert(title: "Error", message: "Failed to modify group: \(error.localizedDescription)")
                    }
                }
            }
        }
    }
    
    private func showAlert(title: String, message: String, completion: (() -> Void)? = nil) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
            completion?()
        })
        present(alert, animated: true)
    }

    @objc private func changeImageTapped() {
        let sheet = UIAlertController(title: "Change Image", message: nil, preferredStyle: .actionSheet)
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            sheet.addAction(UIAlertAction(title: "Camera", style: .default) { _ in
                self.presentImagePicker(source: .camera)
            })
        }
        if UIImagePickerController.isSourceTypeAvailable(.photoLibrary) {
            sheet.addAction(UIAlertAction(title: "Photo Library", style: .default) { _ in
                self.presentImagePicker(source: .photoLibrary)
            })
        }
        sheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        if let pop = sheet.popoverPresentationController {
            pop.sourceView = changeImageButton
            pop.sourceRect = changeImageButton.bounds
        }
        present(sheet, animated: true)
    }
} 

extension ModifyGroupViewController: UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    private func presentImagePicker(source: UIImagePickerController.SourceType) {
        let picker = UIImagePickerController()
        picker.sourceType = source
        picker.delegate = self
        picker.allowsEditing = false
        present(picker, animated: true)
    }
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        picker.dismiss(animated: true)
        if let image = info[.originalImage] as? UIImage {
            selectedImage = image
            imagePreview.image = image
        }
    }
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true)
    }
}

// MARK: - Keyboard Handling
extension ModifyGroupViewController {
    private func setupKeyboardDismissal() {
        // Tap to dismiss
        let tap = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        tap.cancelsTouchesInView = false
        view.addGestureRecognizer(tap)

        // Adjust scroll view for keyboard
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow(_:)), name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide(_:)), name: UIResponder.keyboardWillHideNotification, object: nil)
    }

    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }

    @objc private func keyboardWillShow(_ notification: Notification) {
        guard let frame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect,
              let duration = notification.userInfo?[UIResponder.keyboardAnimationDurationUserInfoKey] as? Double else { return }
        let insets = UIEdgeInsets(top: 0, left: 0, bottom: frame.height, right: 0)
        UIView.animate(withDuration: duration) {
            self.scrollView.contentInset = insets
            self.scrollView.scrollIndicatorInsets = insets
        }
    }

    @objc private func keyboardWillHide(_ notification: Notification) {
        let duration = (notification.userInfo?[UIResponder.keyboardAnimationDurationUserInfoKey] as? Double) ?? 0.25
        UIView.animate(withDuration: duration) {
            self.scrollView.contentInset = .zero
            self.scrollView.scrollIndicatorInsets = .zero
        }
    }
}
