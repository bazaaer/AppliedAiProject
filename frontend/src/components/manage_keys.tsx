import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';  // Import ReactDOM for Portal
import { Button, Input, Typography } from "@material-tailwind/react";
import { useAuth } from "@/context/authContext";
import ApiKeyDisplay from './keyDisplay'; // Import the new component

export function KeyMan() {
    const { apiKey } = useAuth();
    const [keys, setKeys] = useState([]);
    const [newKeyName, setNewKeyName] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [showKeyModal, setShowKeyModal] = useState(false);
    const [newKey, setNewKey] = useState('');

    useEffect(() => {
        const fetchApiKeys = async () => {
            try {
                const response = await fetch('https://klopta.vinnievirtuoso.online/api/api_keys', {
                    headers: {
                        Authorization: `Bearer ${apiKey}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch API keys');
                }

                const data = await response.json();
                const validKeys = data.api_keys.filter((key) => key.status === 'active');
                setKeys(validKeys);
            } catch (error) {
                console.error('Error fetching API keys:', error);
                setErrorMessage('Failed to fetch API keys');
            }
        };

        if (apiKey) {
            fetchApiKeys();
        }
    }, [apiKey]);

    const fetchKeys = async () => {
        try {
            const response = await fetch('https://klopta.vinnievirtuoso.online/api/api_keys', {
                headers: {
                    Authorization: `Bearer ${apiKey}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch API keys');
            }

            const data = await response.json();
            const validKeys = data.api_keys.filter((key) => key.status === 'active');
            setKeys(validKeys);
        } catch (error) {
            console.error('Error fetching API keys:', error);
            setErrorMessage('Failed to fetch API keys');
        }
    }

    const handleCreateKey = async () => {
        if (!newKeyName) {
            setErrorMessage('Key name must be provided!');
            return;
        }

        try {
            const response = await fetch('https://klopta.vinnievirtuoso.online/api/api_keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${apiKey}`,
                },
                body: JSON.stringify({ name: newKeyName }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to create API key');
            }

            const data = await response.json();
            setNewKey(data.api_key);
            setErrorMessage('');
            setNewKeyName('');
            setShowKeyModal(true);  // Open modal after the key is created
        } catch (error) {
            console.error('Error creating API key:', error);
            setErrorMessage(error.message);
        }
    };

    const handleDeleteKey = async (keyName) => {
        try {
            const response = await fetch('https://klopta.vinnievirtuoso.online/api/api_keys', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${apiKey}`,
                },
                body: JSON.stringify({ name: keyName }),
            });

            if (!response.ok) {
                throw new Error('Failed to delete API key');
            }

            setKeys((prevKeys) => prevKeys.filter((key) => key.name !== keyName));
            setErrorMessage('');
        } catch (error) {
            console.error('Error deleting API key:', error);
            setErrorMessage('Failed to delete API key');
        }
    };

    const handleModalClose = () => {
        setShowKeyModal(false);
        fetchKeys();
    };

    return (
        <div className="grid place-items-start justify-center gap-2 max-h-[14rem]">
            {errorMessage && (
                <Typography color="red" className="text-sm">
                    {errorMessage}
                </Typography>
            )}

            <div className="mt-8 flex flex-col items-center justify-center gap-4 md:flex-row">
                <div className="w-80">
                    <Input
                        label="Key name (must be unique)"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                    />
                </div>
                <Button
                    size="md"
                    className="lg:w-max shrink-1"
                    fullWidth
                    color="gray"
                    onClick={handleCreateKey}
                >
                    Create New Key
                </Button>
            </div>

            <div className="mt-8 w-full">
                {keys.length > 0 ? (
                    <ul className='max-h-[10rem] overflow-y-auto p-2'>
                        {keys.map((key, index) => (
                            <li key={index} className="mb-2 flex items-center space-x-2">
                                <div className="flex items-center justify-center w-[40%] p-2 bg-blue-100 rounded-lg">
                                    <p className="text-center">{key.visible_key}</p>
                                </div>
                                <div className="flex items-center justify-center w-[40%] p-2 bg-gray-200 rounded-lg">
                                    <p className="text-center">{key.name}</p>
                                </div>
                                <div className="w-[20%]">
                                    <Button
                                        onClick={() => handleDeleteKey(key.name)}
                                        color="red"
                                        className="w-full"
                                    >
                                        Delete
                                    </Button>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-500">No valid API keys found.</p>
                )}
            </div>

            {showKeyModal && ReactDOM.createPortal(
                <ApiKeyDisplay
                    keyValue={newKey}
                    onClose={handleModalClose}
                    style={{
                        width: `${newKey.length * 8}px`, // Adjust the width based on the key length
                        zIndex: 1000, // Ensure the modal is above other page elements
                    }}
                />,
                document.body // This renders the modal outside the KeyMan component, directly into the body
            )}
        </div>
    );
}
