import React from 'react';
import { Button, Typography } from "@material-tailwind/react";
import { XMarkIcon } from "@heroicons/react/24/solid";

interface ApiKeyDisplayProps {
  keyValue: string;
  onClose: () => void;
}

const ApiKeyDisplay: React.FC<ApiKeyDisplayProps> = ({ keyValue, onClose }) => {
  return (
    <section className="fixed inset-1 flex items-center justify-center bg-black bg-opacity-50 z-[3000]">
      <div className="relative w-full p-2 max-w-min bg-white rounded-lg shadow dark:border dark:bg-gray-800 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <Typography variant="h6">API Key Created</Typography>
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          >
            ✕
          </button>
        </div>
        <Typography className="mt-4">
          The key has been created successfully. Please copy and store it, as it will only be visible once.
        </Typography>
        <div className="mt-4 p-2 bg-gray-100 rounded-lg">
          <Typography variant="body1">{keyValue}</Typography>
        </div>
        <Button color="green" className="mt-4" onClick={onClose}>
          Close
        </Button>
      </div>
    </section>
  );
};

export default ApiKeyDisplay;
