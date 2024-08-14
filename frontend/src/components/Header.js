import React, { useState } from 'react';
import logo from '../assets/hockeyAI.png';

function Header() {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <header className="bg-gray-900 p-4 flex justify-between items-center">
      <div className="w-10"></div> {/* Spacer */}
      <img src={logo} alt="Hockey AI Logo" className="h-12 mx-auto" />
      <div className="relative w-10">
        <button
          onClick={() => setShowInfo(!showInfo)}
          className="bg-blue-500 hover:bg-blue-700 text-white rounded-full w-8 h-8 flex items-center justify-center focus:outline-none"
        >
          i
        </button>
        {showInfo && (
          <div className="absolute right-0 mt-2 w-72 bg-gray-800 text-white rounded-lg shadow-xl p-4 text-sm z-10">
            <h3 className="font-bold mb-2 text-blue-400">Welcome to Hockey AI</h3>
            <p className="mb-2">Your intelligent assistant for NHL statistics and insights, analyzing data from 2008 to 2024.</p>
            <h4 className="font-bold mb-1 text-blue-400">How it works:</h4>
            <ol className="list-decimal list-inside mb-2">
              <li>Ask a question about NHL stats, players, teams, or historical records.</li>
              <li>Our AI processes your query and generates an appropriate SQL query.</li>
              <li>The system retrieves relevant data from our comprehensive NHL database.</li>
              <li>The AI analyzes the retrieved data and formulates a human-readable response.</li>
              <li>You receive a detailed answer with key statistics and insights.</li>
            </ol>
            <p>Whether you're curious about player performances, team statistics, or league trends, Hockey AI is here to assist you with accurate, data-driven answers.</p>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;