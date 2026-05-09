import { Route, Routes } from "react-router-dom"

function App() {
  return (
    <Routes>
      <Route path="/" element={<div className="p-8 text-2xl font-bold">Family Control Panel</div>} />
    </Routes>
  )
}

export default App
