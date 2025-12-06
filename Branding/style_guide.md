
# Python Game Style Guide

## 1. Visual Identity

### 1.1 Core Palette

* Light Grey: #C8C8C8
* Mid Grey: #A0A0A0
* Dark Grey: #707070
* Ocean Blue: #2C82C9
* Emerald Green: #2E8B57
* Amber: #FFB000
* Soft Red: #D65C5C

### 1.2 Pattern Overlay

* Faint embroidered texture
* Pattern colour: #5A5A5A at 8–12 percent opacity
* Applied on large grey backgrounds only

### 1.3 Contrast Rules

* Minimum text contrast 4.5:1
* Accent colours restricted to interactive elements
* Use pattern overlay to avoid flat grey planes

## 2. Typography

### 2.1 Fonts

* Primary: Inter
* Secondary: Roboto Mono

### 2.2 Hierarchy

* H1: 32 px semi-bold
* H2: 24 px semi-bold
* H3: 18 px medium
* Body: 16 px regular
* Mono: 16 px regular

## 3. Layout System

### 3.1 Grid

* Base unit: 8 px
* Padding scale: 8, 16, 24, 32 px

### 3.2 Spacing

* Minimum 16 px margin around element clusters
* Panels use 24 px padding
* No element touches edges

## 4. UI Components

### 4.1 Buttons

* Radius: 4 px
* Primary: Ocean Blue with white text
* Secondary: Emerald Green with white text
* Disabled: #999999 with #DDDDDD text

### 4.2 Panels

* Background: Mid Grey
* Border: Dark Grey at 60 percent opacity
* Pattern overlay: 4 percent opacity

### 4.3 HUD

* Monospace font
* Health: Soft Red
* Energy: Emerald Green
* Currency: Amber

## 5. Iconography

### 5.1 Style

* Line thickness: 2 px
* Colour: Dark Grey
* Filled for active state
* Outline for inactive

### 5.2 Icons

* Settings: Cog
* Inventory: Grid
* Map: Compass
* Dialogue: Speech bubble

## 6. Environment Art Direction

### 6.1 Surfaces

* Use the grey palette
* Apply faint embroidered pattern
* Pattern density below 15 percent

### 6.2 Colour Use

* Accents used for landmarks, lights, collectibles, signs
* Accents capped at 20 percent of screen area

## 7. Animations

### 7.1 Timing

* Standard durations: 120 ms, 240 ms, 360 ms
* Easing: cubic-in-out

### 7.2 Motion

* Hover: minor colour shift
* Press: 95 percent scale then return
* Panels: fade in at 240 ms

## 8. Sound

### 8.1 Effects

* UI click: soft digital click
* Error: low-frequency dampened blip
* Events: light synth tones

### 8.2 Levels

* Peak at -10 dB
* All effects normalised

## 9. Code Style (Python)

### 9.1 Naming

* snake_case for variables and functions
* PascalCase for classes
* UPPER_CASE for constants

### 9.2 Structure

* Prefer one class per file
* Use pure functions for utilities
* Comments for intent only

### 9.3 Asset Paths

* /assets/images/
* /assets/sounds/
* /assets/fonts/

## 10. Accessibility

### 10.1 Colour Blind Support

* Provide pattern alternatives
* Avoid red and green exclusivity

### 10.2 Text Size

* Scaling factor 1.0 to 1.6

### 10.3 Input

* Full remapping
* Configurable hold durations

## 11. Consistency

* Accent colours used sparingly
* Pattern always subtle
* Strict adherence to 8 px grid
* No pure white or pure black
* Irish English spellings used throughout
