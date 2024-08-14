import React from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import backgroundImage from './assets/hockey_background.jpg';
import { fetchQuery } from './api'; // Import the fetchQuery function

function App() {
  const handleQuery = async (query) => {
    try {
      const data = await fetchQuery(query);
      return data.natural_language_answer;
    } catch (error) {
      console.error('Error fetching response:', error);
      return 'Sorry, there was an error processing your query.';
    }
  };

  return (
    <div className="h-screen bg-cover bg-center flex flex-col" 
         style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className="flex-grow flex flex-col m-4 overflow-hidden rounded-lg bg-gray-900 bg-opacity-80">
        <Header />
        <ChatContainer onQuery={handleQuery} />
      </div>
    </div>
  );
}

export default App;