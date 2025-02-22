import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Leaderboard from './pages/Leaderboard'

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path='/'
          element={
            <Leaderboard route='/data_manager/requestdata/' />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
