import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ProtectedRoute from "../../components/ProtectedRoute";
import * as AuthContextModule from "../../contexts/AuthContext";

jest.mock("../../contexts/AuthContext", () => ({
  ...jest.requireActual("../../contexts/AuthContext"),
  useAuth: jest.fn(),
}));

describe("ProtectedRoute", () => {
  it("redirects to /login when not authenticated", () => {
    AuthContextModule.useAuth.mockReturnValue({
      authenticated: false,
      loading: false,
    });

    render(
      <MemoryRouter initialEntries={["/quiz"]}>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    );

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("renders children when authenticated", () => {
    AuthContextModule.useAuth.mockReturnValue({
      authenticated: true,
      loading: false,
    });

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    );

    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });

  it("shows loading while checking auth", () => {
    AuthContextModule.useAuth.mockReturnValue({
      authenticated: false,
      loading: true,
    });

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>,
    );

    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });
});
