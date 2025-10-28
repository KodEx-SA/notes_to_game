import React, { useState } from 'react';
import Upload from './components/Upload.jsx';
import Game from './components/Game.jsx';

function App() {
  const [keywords, setKeywords] = useState([]);

  return (
    <div>
      <h1>Notes to Game</h1>
      <Upload setKeywords={setKeywords} />
      {keywords.length > 0 && <Game keywords={keywords} />}
    </div>
  );
}

export default App;