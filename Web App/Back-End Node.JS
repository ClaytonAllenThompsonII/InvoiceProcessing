// Make sure to replace 'YOUR_ACCESS_KEY_ID', 'YOUR_SECRET_ACCESS_KEY', 'YOUR_AWS_REGION', and 'your-s3-bucket-name' with actual AWS credentials and S3 bucket information. 
// To run this, set up a Node.js environment, install the required packages (Express, Multer, and AWS SDK), and run the Node.js server. 
// Users can visit the landing page, upload invoices, and the server will upload the invoices to the specified S3 bucket.

// Also, this is a basic example and doesn't include error handling or security features that you would need in a production environment.
// Additionally, consider implementing authentication and security features for a production-ready application, especially when dealing with file uploads.


const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const app = express();
const port = 3000;

// Configure AWS SDK with your credentials and region
const s3 = new AWS.S3({
    accessKeyId:     'YOUR_ACCESS_KEY_ID',
    secretAccessKey: 'YOUR_SECRET_ACCESS_KEY',
    region:          'YOUR_AWS_REGION'
});

// Set up multer for handling file uploads
const upload = multer({ dest: 'uploads/' });

app.use(express.static('public'));

// Handle POST requests for file upload
app.post('/upload', upload.single('invoice'), (req, res) => {
    if (!req.file) {
        res.status(400).send('No file uploaded.');
        return;
    }

    const params = {
        Bucket: 's3-bucket-name',  // Replace with your S3 bucket name
        Key: req.file.originalname,
        Body: req.file.buffer
    };

    // Upload the file to the specified S3 bucket
    s3.upload(params, (err, data) => {
        if (err) {
            res.status(500).send('Error uploading the file.');
        } else {
            res.status(200).send('File uploaded successfully!');
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
