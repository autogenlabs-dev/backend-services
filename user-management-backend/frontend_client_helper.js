// Frontend client helper for verifying user with Clerk token
// Place this in your Next.js frontend (e.g., in a utils or lib folder)

import { getToken } from "@clerk/nextjs";

/**
 * Verifies the current user's Clerk session by posting the JWT to the backend.
 * @param {string} backendUrl - The backend base URL (e.g., "http://localhost:8000")
 * @returns {Promise<Object>} - Response containing verification status and user data
 */
export async function verifyUserWithClerk(backendUrl = "http://localhost:8000") {
  try {
    // Get the Clerk session JWT
    const token = await getToken();

    if (!token) {
      throw new Error("No Clerk token available. User may not be logged in.");
    }

    // POST the token to the backend's /api/verify-user endpoint
    const response = await fetch(`${backendUrl}/api/verify-user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(`Verification failed: ${data.detail || response.statusText}`);
    }

    return data; // { verified: true, user: {...}, claims: {...} }
  } catch (error) {
    console.error("User verification error:", error);
    throw error;
  }
}

// Alternative: Call your Next.js API route (if you have one set up)
// This proxies through your frontend to the backend
export async function verifyUserViaFrontendAPI() {
  try {
    // Get the Clerk session JWT
    const token = await getToken();

    if (!token) {
      throw new Error("No Clerk token available. User may not be logged in.");
    }

    // POST to your Next.js API route at /api/verify-user
    const response = await fetch("/api/verify-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(`Verification failed: ${data.error || response.statusText}`);
    }

    return data; // { ok: true, status: 200, backendBody: {...}, clerk: {...} }
  } catch (error) {
    console.error("User verification error:", error);
    throw error;
  }
}

// Example usage in a React component:
//
/*
import { useEffect, useState } from "react";
import { verifyUserWithClerk } from "../lib/verifyUser";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      try {
        const result = await verifyUserWithClerk();
        setUser(result.user);
      } catch (error) {
        console.error("Failed to verify user:", error);
        // Handle error (e.g., redirect to login)
      } finally {
        setLoading(false);
      }
    };

    verifyUser();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <p>Email: {user?.email}</p>
    </div>
  );
}
*/