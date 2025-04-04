const express = require("express");
const fs = require("fs");
const { spawn } = require("child_process");

const app = express();
const PORT = 3000;

app.use(express.json());

app.get("/", (req, res) => {
    res.send("App is working");
});

app.post("/analyze", (req, res) => {
    if (!req.body.csvData) {
        return res.status(400).send("CSV data is required");
    }

    // Save CSV data to a file
    fs.writeFileSync("sample.csv", req.body.csvData);

    // Execute the Python script
    const pythonProcess = spawn("python3", ["sample.py"]);

    pythonProcess.on("close", (code) => {
        if (code === 0) {
            // Send the output file as a response
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

app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
