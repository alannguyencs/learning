import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "../../contexts/AuthContext";
import apiService from "../../services/api";

jest.mock("../../services/api");

const TestConsumer = () => {
  const { user, authenticated, loading, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(loading)}</span>
      <span data-testid="authenticated">{String(authenticated)}</span>
      <span data-testid="username">{user?.username || "none"}</span>
      <button data-testid="login-btn" onClick={() => login("test", "pass")}>
        Login
      </button>
      <button data-testid="logout-btn" onClick={logout}>
        Logout
      </button>
    </div>
  );
};

describe("AuthProvider", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("defaults to unauthenticated", async () => {
    apiService.getCurrentUser.mockResolvedValue({ authenticated: false });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("username").textContent).toBe("none");
  });

  it("restores session from /api/me", async () => {
    apiService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 1, username: "testuser" },
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("authenticated").textContent).toBe("true");
    });

    expect(screen.getByTestId("username").textContent).toBe("testuser");
  });

  it("login sets user and authenticated", async () => {
    apiService.getCurrentUser.mockResolvedValue({ authenticated: false });
    apiService.login.mockResolvedValue({
      success: true,
      user: { id: 1, username: "testuser" },
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });

    await act(async () => {
      screen.getByTestId("login-btn").click();
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("true");
    expect(screen.getByTestId("username").textContent).toBe("testuser");
  });

  it("logout clears state", async () => {
    apiService.getCurrentUser.mockResolvedValue({
      authenticated: true,
      user: { id: 1, username: "testuser" },
    });
    apiService.logout.mockResolvedValue({});

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("authenticated").textContent).toBe("true");
    });

    await act(async () => {
      screen.getByTestId("logout-btn").click();
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("username").textContent).toBe("none");
  });

  it("useAuth throws outside provider", () => {
    const ThrowingComponent = () => {
      useAuth();
      return null;
    };

    const consoleSpy = jest.spyOn(console, "error").mockImplementation();
    expect(() => render(<ThrowingComponent />)).toThrow(
      "useAuth must be used within AuthProvider",
    );
    consoleSpy.mockRestore();
  });
});
