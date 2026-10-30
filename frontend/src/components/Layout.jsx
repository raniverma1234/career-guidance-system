import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

// Every page sits inside this frame: navigation bar on top, footer at the bottom
export default function Layout() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="container">
        <Outlet />
      </main>
      <footer className="footer">
        AI-Powered Personalized Career Guidance and Skill Development System. Match scores are
        project-defined indicators, not guarantees.
      </footer>
    </div>
  );
}
