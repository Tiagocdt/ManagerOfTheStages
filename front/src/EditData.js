import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Page.css';
import LoginModal from './LoginModal';
import './LoginModal.css';

const EditData = () => {
  const [entries, setEntries] = useState([]);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const fetchEntries = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/get-entries');
      setEntries(response.data);
    } catch (error) {
      console.error('Error fetching entries:', error);
      if (error.response && error.response.status === 401) {
        alert('Session expired. Please log in again.');
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setIsAuthenticated(false);
        setIsLoginOpen(true);
      }
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      setIsLoginOpen(false);
      fetchEntries();
    } else {
      setIsLoginOpen(true);
    }
  }, []);

  const handleLogin = async (username, password) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/login', {
        username,
        password,
      });
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
      setIsLoginOpen(false);
      fetchEntries();
    } catch (error) {
      alert('Invalid credentials. Please try again.');
    }
  };

  const handleModalClose = () => {
    setIsLoginOpen(false);
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/delete-entry/${id}`);
      setEntries(entries.filter((entry) => entry.id !== id));
    } catch (error) {
      console.error('Error deleting entry:', error);
      if (error.response && error.response.status === 401) {
        alert('Session expired. Please log in again.');
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setIsAuthenticated(false);
        setIsLoginOpen(true);
      }
    }
  };

  const [editEntryId, setEditEntryId] = useState(null);
  const [editFormData, setEditFormData] = useState({
    species: '',
    temperature: '',
    stage: '',
    development_time_hpf: '',
  });

  const handleEditClick = (entry) => {
    setEditEntryId(entry.id);
    setEditFormData(entry);
  };

  const handleEditFormChange = (e) => {
    setEditFormData({ ...editFormData, [e.target.name]: e.target.value });
  };

  const handleCancelClick = () => {
    setEditEntryId(null);
  };

  const handleSaveClick = async () => {
    try {
      await axios.put(`http://127.0.0.1:5000/update-entry/${editEntryId}`, editFormData);
      setEntries(
        entries.map((entry) =>
          entry.id === editEntryId ? { ...editFormData, id: editEntryId } : entry
        )
      );
      setEditEntryId(null);
    } catch (error) {
      console.error('Error updating entry:', error);
      if (error.response && error.response.status === 401) {
        alert('Session expired. Please log in again.');
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setIsAuthenticated(false);
        setIsLoginOpen(true);
      }
    }
  };

  return (
    <>
      <div className={`edit-data-container ${isLoginOpen ? 'blur-background' : ''}`}>
        <div className="page-container">
          <div className="form-section">
            <h2>Edit Data</h2>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Species</th>
                  <th>Temperature</th>
                  <th>Stage</th>
                  <th>Development Time (hpf)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.id}>
                    {editEntryId === entry.id ? (
                      <>
                        <td>{entry.id}</td>
                        <td>
                          <input
                            type="text"
                            name="species"
                            value={editFormData.species}
                            onChange={handleEditFormChange}
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            name="temperature"
                            value={editFormData.temperature}
                            onChange={handleEditFormChange}
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            name="stage"
                            value={editFormData.stage}
                            onChange={handleEditFormChange}
                          />
                        </td>
                        <td>
                          <input
                            type="text"
                            name="development_time_hpf"
                            value={editFormData.development_time_hpf}
                            onChange={handleEditFormChange}
                          />
                        </td>
                        <td>
                          <button onClick={handleSaveClick} className="submit-btn">
                            Save
                          </button>
                          <button onClick={handleCancelClick} className="cancel-btn">
                            Cancel
                          </button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td>{entry.id}</td>
                        <td>{entry.species}</td>
                        <td>{entry.temperature}</td>
                        <td>{entry.stage}</td>
                        <td>{entry.development_time_hpf}</td>
                        <td>
                          <button onClick={() => handleEditClick(entry)} className="edit-btn">
                            Edit
                          </button>
                          <button onClick={() => handleDelete(entry.id)} className="remove-btn">
                            Delete
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={handleModalClose}
        onLogin={handleLogin}
      />
    </>
  );
};

export default EditData;
