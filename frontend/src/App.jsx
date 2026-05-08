import {BrowserRouter, Routes, Route} from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import BakeriesPage from "./pages/BakeriesPage";
import BakeryMenuPage from "./pages/BakeryMenuPage";
import RegisterPage from "./pages/RegisterPage";


function App() {
  return (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/bakeries" element={<BakeriesPage />} />
      <Route path="/bakeries/:bakery_id" element={<BakeryMenuPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Routes>
  </BrowserRouter>
  );
}

export default App;