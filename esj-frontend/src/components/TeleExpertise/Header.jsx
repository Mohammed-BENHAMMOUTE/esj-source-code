"use client";
import "@/assets/css/style.css";
import Link from "next/link";
import { useEffect } from "react";
import {
  logo,
  baricon,
  baricon1,
  searchnormal,
  imguser,
  noteicon,
  user06,
  settingicon01,
  noteicon1,
} from "./imagepath";
import Image from "next/image";

const Header = () => {
  
  useEffect(() => {
    require("bootstrap/dist/js/bootstrap.bundle.min.js");
  }, []);

  const handlesidebar = () => {
    document.body.classList.toggle("mini-sidebar");
  };

  const handlesidebarmobilemenu = () => {
    document.body.classList.toggle("slide-nav");
    document.getElementsByTagName("html")[0].classList.toggle("menu-opened");
    /*document
      .getElementsByClassName("sidebar-overlay")[0]
      .classList.toggle("opened");*/
  };

  const openDrawer = () => {
    const div = document.querySelector(".main-wrapper");
    if (div?.className?.includes("open-msg-box")) {
      div?.classList?.remove("open-msg-box");
    } else {
      div?.classList?.add("open-msg-box");
    }
  };

  useEffect(() => {
    const handleClick = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
      } else {
        if (document.exitChaimaAitAliFullscreen) {
          document.exitFullscreen();
        }
      }
    };

    const maximizeBtn = document.querySelector(".win-maximize");
    // maximizeBtn.addEventListener('click', handleClick);

    return () => {
      // maximizeBtn.removeEventListener('click', handleClick);
    };
  }, []);
  return (
    <div className="main-wrapper">
      <div className="header">
        <div className="header-left">
          <Link href="/TeleExpertise" className="logo">
            <Image src={logo} width={35} height={35} alt="" />{" "}
            <span>TéléExpertise</span>
          </Link>
        </div>
        <Link
          href="#"
          id="toggle_btn"
          onClick={handlesidebar}
          
        >
          <Image src={baricon} alt="" style={{marginLeft:"30px",marginTop:"100px"}}/>
        </Link>
        <Link
          href="#"
          id="mobile_btn"
          className="mobile_btn float-start"
          onClick={handlesidebarmobilemenu}
          style={{ marginTop: "28px" }}
        >
          <Image src={baricon1} alt="" />
        </Link>

        <ul className="nav user-menu float-end">
          <li className="nav-item dropdown d-none d-sm-block">
            <Link
              href="/"
              className="dropdown-toggle nav-link"
              data-bs-toggle="dropdown"
            >
              <Image style={{ marginTop: "25px" }} src={noteicon1} alt="" />
              <span className="pulse" />
            </Link>
            <div className="dropdown-menu notifications">
              <div className="topnav-dropdown-header">
                <span>Notifications</span>
              </div>
              <div className="drop-scroll">
                <ul className="notification-list">
                  {notifications.map((notification) => (
                    <li key={notification.id} className="notification-message">
                      <Link href={notification.href}>
                        <div className="media">
                          <span className="avatar">{notification.avatar}</span>
                          <div className="media-body">
                            <p className="noti-details">
                              <span className="noti-title">
                                {notification.user}
                              </span>{" "}
                              {notification.action}{" "}
                              {notification.additional &&
                                notification.additional.map((name, index) => (
                                  <span key={index} className="noti-title">
                                    {name}
                                    {index <
                                      notification.additional.length - 1 &&
                                      " and "}
                                  </span>
                                ))}
                              {notification.task && (
                                <span className="noti-title">
                                  {notification.task}
                                </span>
                              )}
                            </p>
                            <p className="noti-time">
                              <span className="notification-time">
                                {notification.time}
                              </span>
                            </p>
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="topnav-dropdown-footer">
                <Link href="/">View all Notifications</Link>
              </div>
            </div>
          </li>
          {/* <li className="nav-item dropdown d-none d-sm-block">
            <Link
              href="/"
              onClick={openDrawer}
              id="open_msg_box"
              className="hasnotifications nav-link"
            >
              <Image src={noteicon} alt="" />
              <span className="pulse" />{" "}
            </Link>
          </li> */}
          <li className="nav-item dropdown has-arrow user-profile-list">
            <Link
              href="/"
              className="dropdown-toggle nav-link user-link"
              data-bs-toggle="dropdown"
            >
              <div className="user-names">
                <h5>Ahmad Berada </h5>
              </div>
              {/* <span className="user-img">
                <Image src={user06} alt="Admin"/>
              </span> */}
              <Image src={user06} alt="Admin" className="user-img" />
            </Link>
            <div className="dropdown-menu">
              <Link href="/" className="dropdown-item">
                Mon profil
              </Link>
              <Link href="/" className="dropdown-item">
                Modifier le profil
              </Link>
              <Link href="/" className="dropdown-item">
                Paramètres
              </Link>
              <Link href="/" className="dropdown-item">
                Se Déconnecter
              </Link>
            </div>
          </li>
          {/* <li className="nav-item ">
            <Link href="/Parametres" className="hasnotifications nav-link">
              <Image src={settingicon01} alt="" />{" "}
            </Link>
          </li> */}
        </ul>
        <div className="dropdown mobile-user-menu float-end">
          <Link
            href="/"
            className="dropdown-toggle"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i className="fa-solid fa-ellipsis-vertical" />
          </Link>
          <div className="dropdown-menu dropdown-menu-end">
            <Link href="/" className="dropdown-item">
              My Profile
            </Link>
            <Link href="/" className="dropdown-item">
              Edit Profile
            </Link>
            <Link href="/" className="dropdown-item">
              Settings
            </Link>
            <Link href="/" className="dropdown-item">
              Logout
            </Link>
          </div>
        </div>
      </div>

      {/* messages */}
      {/*
      <div className="notification-box">
        <div className="msg-sidebar notifications msg-noti">
          <div className="topnav-dropdown-header">
            <span>Messages</span>
          </div>
          <div className="drop-scroll msg-list-scroll" id="msg_list">
            <ul className="list-box">
              {messages.map((message) => (
                <li key={message.id}>
                  <Link href={message.href}>
                    <div
                      className={`list-item ${
                        message.newMessage ? "new-message" : ""
                      }`}
                    >
                      <div className="list-left">
                        <span className="avatar">{message.avatar}</span>
                      </div>
                      <div className="list-body">
                        <span className="message-author">{message.author}</span>
                        <span className="message-time">{message.time}</span>
                        <div className="clearfix"></div>
                        <span className="message-content">
                          {message.content}
                        </span>
                      </div>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="topnav-dropdown-footer">
            <Link href="/">See all messages</Link>
          </div>
        </div>
      </div>*/}
      <style jsx>{`
        @media only screen and (max-width: 768px) {
          .header-left {
            margin-left: -100px;
          }
        }
      `}</style>
    </div>
  );
};

export default Header;
