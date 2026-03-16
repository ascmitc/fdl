// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file version.ts
 * @brief FDL document version (major, minor).
 */

export class Version {
  readonly major: number;
  readonly minor: number;
  readonly patch: number;

  constructor(major: number = 2, minor: number = 0, patch: number = 0) {
    this.major = major;
    this.minor = minor;
    this.patch = patch;
  }

  equals(other: Version): boolean {
    return (
      this.major === other.major &&
      this.minor === other.minor &&
      this.patch === other.patch
    );
  }

  toString(): string {
    return `Version(major=${this.major}, minor=${this.minor}, patch=${this.patch})`;
  }
}
