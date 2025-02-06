import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainScreen from './MainScreen/MainScreen';
import Login from './Login';
import './App.css';

export default function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/chat" element={<MainScreen />} />
      </Routes>
    </BrowserRouter>
  )
}