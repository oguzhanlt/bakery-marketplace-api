import {BrowserRouter, Routes, Route} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import BakeriesPage from "./pages/BakeriesPage";

function App() {
  return (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/bakeries" element={<BakeriesPage />} />
    </Routes>
  </BrowserRouter>
  );
}

export default App;