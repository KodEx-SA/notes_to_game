import React, { useState } from 'react';
import axios from 'axios';

const Upload = ({ setKeywords }) => {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    if (file.size === 0) {
      alert("This file is empty. Please choose a file with content.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', 'anonymous'); // Replace with auth later

    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setKeywords(response.data.keywords);
    } catch (error) {
      console.error('Upload error:', error);
      alert(error.response?.data?.error || 'Failed to process file');
    }
  };

  return (
    <div className="upload-container">
      <input
        type="file"
        accept=".txt,.pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload}>Upload Notes</button>
    </div>
  );
};

export default Upload;