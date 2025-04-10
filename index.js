const express = require("express");
const multer = require("multer");
const cors = require("cors");
const { spawn } = require("child_process");

const app = express();
const PORT = 3000;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Configure multer storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      cb(null, "./"); 
    },
    filename: (req, file, cb) => {
      if (file.fieldname === "file1") {
        cb(null, "X.csv");
      } else if (file.fieldname === "file2") {
        cb(null, "edge_index.csv");
      } else {
        cb(null, file.originalname);
      }
    },
  });
  

const upload = multer({ storage });

// Health check endpoint
app.get("/", (req, res) => {
    res.send("App is working");
});

// Upload endpoint for two files
app.post("/upload", upload.fields([
    { name: "file1", maxCount: 1 },
    { name: "file2", maxCount: 1 }
]), (req, res) => {
    if (!req.files || !req.files.file1 || !req.files.file2) {
        return res.status(400).send("Both files are required.");
    }

    console.log("File 1 path:", req.files.file1[0].path);
    console.log("File 2 path:", req.files.file2[0].path);

    res.status(200).send("Files uploaded successfully");
});

// Analyze endpoint that runs run.py and sends output.csv
app.post("/analyze", (req, res) => {
    const pythonProcess = spawn("python3", ["run.py"]);

    pythonProcess.on("close", (code) => {
        if (code === 0) {
            res.download("output.csv", "output.csv", (err) => {
                if (err) {
                    res.status(500).send("Error sending file");
                }
            });
        } else {
            res.status(500).send("Error processing CSV");
        }
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`Python error: ${data}`);
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
