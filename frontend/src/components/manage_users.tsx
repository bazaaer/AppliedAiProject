import React, { useState, useEffect } from 'react';
import { Button, Input, Select, Option, Typography } from '@material-tailwind/react';
import { useAuth } from "@/context/authContext";

export function UserMan() {
    const { apiKey } = useAuth();
    const [users, setUsers] = useState([]);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [usertype, setUsertype] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const savedUsername = localStorage.getItem("username");

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await fetch('https://klopta.vinnievirtuoso.online/api/users', {
                    headers: {
                        Authorization: `Bearer ${apiKey}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch users');
                }

                const data = await response.json();
                setUsers(data.users.filter(user => user.username !== 'admin' && user.username !== 'temp' && user.username !== savedUsername));
            } catch (error) {
                console.error('Error fetching users:', error);
                setErrorMessage('Error fetching users.');
            }
        };

        if (apiKey) {
            fetchUsers();
        }
    }, [apiKey]);

    const handleCreateUser = async () => {
        if (!username || !password || !usertype) {
            setErrorMessage("All fields must be filled out!");
            return;
        }

        try {
            const response = await fetch('https://klopta.vinnievirtuoso.online/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${apiKey}`,
                },
                body: JSON.stringify({ username, password, role: usertype }),
            });

            if (!response.ok) {
                throw new Error('Failed to create user');
            }

            const data = await response.json();
            setErrorMessage('');
            setUsers((prevUsers) => [...prevUsers, { username, role: usertype }]);
        } catch (error) {
            console.error('Error creating user:', error);
            setErrorMessage('Failed to create user');
        }
    };

    const handleDeleteUser = async (username) => {
        try {
            const response = await fetch(`https://klopta.vinnievirtuoso.online/api/users`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${apiKey}`,
                },
                body: JSON.stringify({ "username":username }),
            });

            if (!response.ok) {
                throw new Error('Failed to delete user');
            }

            setUsers((prevUsers) => prevUsers.filter((user) => user.username !== username));
            setErrorMessage('');
        } catch (error) {
            console.error('Error deleting user:', error);
            setErrorMessage('Failed to delete user');
        }
    };

    return (
        <div className="grid place-items-start justify-center gap-2 max-h-[14rem]">
            {errorMessage && (
                <Typography color="red" className="text-sm">
                    {errorMessage}
                </Typography>
            )}

            <div className="w-full h-[8rem] rounded-lg bg-gray-100 p-3 overflow-y-scroll">
                {users.length > 0 ? (
                    <ul>
                        {users.map((user, index) => (
                            <li key={index} className="mb-2 flex items-center space-x-2">
                                <div className="flex items-center justify-center w-[44%] p-2 bg-blue-100 rounded-lg">
                                    <p className="text-center">{user.username}</p>
                                </div>
                                <div className="flex items-center justify-center w-[22%] p-2 bg-gray-200 rounded-lg">
                                    <p className="text-center">{user.role}</p>
                                </div>
                                <div className="w-[30%] h-full">
                                    <Button
                                        onClick={() => handleDeleteUser(user.username)}
                                        color="red"
                                        className="w-[50%] h-full"
                                    >
                                        Delete
                                    </Button>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-gray-500">No users found.</p>
                )}
            </div>

            <div className="mt-4 flex flex-col items-center justify-center gap-4 md:flex-row">
                <div className="flex flex-col gap-2">
                    <div className="w-80">
                        <Input
                            label="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="w-80">
                        <Input
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                </div>
                <div>
                    <Select
                        label="User Type"
                        value={usertype}
                        onChange={(value) => setUsertype(value)}
                    >
                        <Option value="admin">Admin</Option>
                        <Option value="user">User</Option>
                    </Select>
                </div>
                <Button
                    size="md"
                    className="lg:w-max shrink-1"
                    fullWidth
                    color="gray"
                    onClick={handleCreateUser}
                >
                    Create New User
                </Button>
            </div>
        </div>
    );
}
