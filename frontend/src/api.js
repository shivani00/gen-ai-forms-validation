import axios from "axios";
export const validateForm = async (formData) => {
  console.log("Sending form data to backend for validation...");
  const response = await axios.post(
    "http://localhost:8000/validate",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );

  return response.data;
};