/**
 * SDK errors mirroring the API error envelope (10-api-contracts).
 *
 * The server renders failures as `{ error: { code, message, details } }`. The
 * transport parses that and throws the matching subclass, so callers can catch
 * `NotFoundError` / `ValidationError` specifically or `ApiError` for any failure.
 */

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(
    status: number,
    code: string,
    message: string,
    details: Record<string, unknown> = {},
  ) {
    super(`[${status} ${code}] ${message}`);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export class NotFoundError extends ApiError {
  constructor(status: number, code: string, message: string, details?: Record<string, unknown>) {
    super(status, code, message, details);
    this.name = "NotFoundError";
  }
}

export class ValidationError extends ApiError {
  constructor(status: number, code: string, message: string, details?: Record<string, unknown>) {
    super(status, code, message, details);
    this.name = "ValidationError";
  }
}
