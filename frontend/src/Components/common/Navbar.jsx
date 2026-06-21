import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../../assets/images/logo1.png";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser, faChalkboardUser } from "@fortawesome/free-solid-svg-icons";
import { authService } from "../../api/auth.service";
import { useUserContext } from "../../contexts/UserContext";

function Navbar(props) {
  const value = props.page;
  const navigate = useNavigate();
  const { isAuthenticated, setUser } = useUserContext();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogOut = async () => {
    await authService.logout();
    setUser(null);
    navigate("/login");
  };

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  return (
    <div>
      <nav className="bg-white w-full flex flex-row justify-between items-center px-[4vw] py-2 shadow-[2px_2px_10px_rgba(0,0,0,0.15)] z-[999]">

        {/* LOGO - FIXED SIZE */}
        <div className="flex items-center">
          <img
            src={logo}
            alt="Nexora Logo"
            style={{ height: "70px", width: "auto", objectFit: "contain" }}
            className="cursor-pointer"
          />
        </div>

        <div className="flex">
          <div id="menu-btn" className="hidden">
            <div className="menu-dash" onClick={toggleMobileMenu}>&#9776;</div>
          </div>
          <i id="menu-close" className="fas fa-times hidden" onClick={closeMobileMenu}></i>

          <ul className={`flex justify-end items-center ${isMobileMenuOpen ? "active" : ""}`}>

            {isMobileMenuOpen && (
              <li className="close-button">
                <button onClick={closeMobileMenu}>X</button>
              </li>
            )}

            {/* HOME */}
            {value === "home" ? (
              <li className="list-none ml-5 rounded-[5px] bg-gradient-to-r from-blue-600 to-purple-600">
                <Link to={"/"} className="no-underline text-white text-[17px] font-bold px-[10px] py-[2px] block hover:text-yellow-400">
                  Home
                </Link>
              </li>
            ) : (
              <li className="list-none ml-5">
                <Link to={"/"} className="no-underline text-[rgb(21,21,100)] text-[17px] font-bold hover:text-yellow-400">
                  Home
                </Link>
              </li>
            )}

            {/* COURSES */}
            {value === "courses" ? (
              <li className="list-none ml-5 rounded-[5px] bg-gradient-to-r from-blue-600 to-purple-600">
                <Link to={"/courses"} className="no-underline text-white text-[17px] font-bold px-[10px] py-[2px] block hover:text-yellow-400">
                  Courses
                </Link>
              </li>
            ) : (
              <li className="list-none ml-5">
                <Link to={"/courses"} className="no-underline text-[rgb(21,21,100)] text-[17px] font-bold hover:text-yellow-400">
                  Courses
                </Link>
              </li>
            )}

            {/* PROFILE */}
            {isAuthenticated && (
              value === "profile" ? (
                <li className="list-none ml-5 rounded-[5px] bg-gradient-to-r from-blue-600 to-purple-600">
                  <Link to={"/profile"} className="no-underline text-white text-[17px] font-bold px-[10px] py-[2px] block hover:text-yellow-400">
                    Profile <FontAwesomeIcon icon={faUser} className="ml-1" />
                  </Link>
                </li>
              ) : (
                <li className="list-none ml-5">
                  <Link to={"/profile"} className="no-underline text-[rgb(21,21,100)] text-[17px] font-bold hover:text-yellow-400">
                    Profile <FontAwesomeIcon icon={faUser} className="ml-1" />
                  </Link>
                </li>
              )
            )}

            {/* LEARNINGS */}
            {isAuthenticated && (
              value === "learnings" ? (
                <li className="list-none ml-5 rounded-[5px] bg-gradient-to-r from-blue-600 to-purple-600">
                  <Link to={"/learnings"} className="no-underline text-white text-[17px] font-bold px-[10px] py-[2px] block hover:text-yellow-400">
                    Learnings <FontAwesomeIcon icon={faChalkboardUser} className="ml-1" />
                  </Link>
                </li>
              ) : (
                <li className="list-none ml-5">
                  <Link to={"/learnings"} className="no-underline text-[rgb(21,21,100)] text-[17px] font-bold hover:text-yellow-400">
                    Learnings <FontAwesomeIcon icon={faChalkboardUser} className="ml-1" />
                  </Link>
                </li>
              )
            )}

            {/* LOGIN / LOGOUT */}
            {isAuthenticated ? (
              <li className="list-none ml-5">
                <button
                  onClick={handleLogOut}
                  className="w-[120px] h-[35px] bg-[#0047ca] rounded-lg text-white text-[15px] hover:bg-[#002c5fe1]"
                >
                  Sign Out
                </button>
              </li>
            ) : (
              <li className="list-none ml-5">
                <button
                  onClick={() => navigate("/login")}
                  className="w-[120px] h-[35px] bg-[#0047ca] rounded-lg text-white text-[15px] hover:bg-[#002c5fe1]"
                >
                  Login/SignUp
                </button>
              </li>
            )}

          </ul>
        </div>
      </nav>
    </div>
  );
}

export default Navbar;