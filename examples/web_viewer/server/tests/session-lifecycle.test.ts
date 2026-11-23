// SPDX-License-Identifier: Apache-2.0
/** Sessions hold native FDL documents, which must be closed when they expire. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import {
  evictExpiredSessions,
  getSession,
  parseFdlFromString,
} from "../src/services/fdl-service.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../..");
const entries = JSON.parse(readFileSync(path.join(here, "scenario_inputs.json"), "utf-8"));
const sourceJson = readFileSync(path.join(repoRoot, entries[0].sourceFdl), "utf-8");

const THIRTY_ONE_MINUTES_MS = 31 * 60 * 1000;

describe("FDL session lifecycle", () => {
  it("closes and removes sessions older than the TTL", () => {
    const { sessionId } = parseFdlFromString(sourceJson);
    const session = getSession(sessionId);
    assert.ok(session);
    assert.equal(session.fdl.isClosed, false);

    evictExpiredSessions(Date.now() + THIRTY_ONE_MINUTES_MS);

    assert.equal(getSession(sessionId), undefined, "expired session should be removed");
    assert.equal(session.fdl.isClosed, true, "expired session's document should be closed");
  });

  it("keeps sessions that have not expired", () => {
    const { sessionId } = parseFdlFromString(sourceJson);
    const session = getSession(sessionId);
    assert.ok(session);

    evictExpiredSessions(Date.now());

    assert.ok(getSession(sessionId), "fresh session should be kept");
    assert.equal(session.fdl.isClosed, false);
    session.fdl.close();
  });
});
