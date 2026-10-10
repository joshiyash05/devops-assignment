def build_openapi_spec():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "ACEest Fitness & Gym API",
            "version": "1.0.0",
            "description": "No-UI Flask API for gym client, program, and workout management.",
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Check service health",
                    "responses": {
                        "200": {
                            "description": "Service is running",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Health"}
                                }
                            },
                        }
                    },
                }
            },
            "/programs": {
                "get": {
                    "summary": "List available fitness programs",
                    "responses": {
                        "200": {
                            "description": "Program list",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "programs": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Program"
                                                },
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/clients": {
                "get": {
                    "summary": "List clients",
                    "responses": {
                        "200": {
                            "description": "Client list",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "clients": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Client"
                                                },
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a client",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ClientInput"}
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Client created"},
                        "400": {"description": "Validation error"},
                    },
                },
            },
            "/clients/{client_id}": {
                "get": {
                    "summary": "Get one client",
                    "parameters": [{"$ref": "#/components/parameters/ClientId"}],
                    "responses": {
                        "200": {"description": "Client details"},
                        "404": {"description": "Client not found"},
                    },
                }
            },
            "/clients/{client_id}/summary": {
                "get": {
                    "summary": "Get client summary",
                    "parameters": [{"$ref": "#/components/parameters/ClientId"}],
                    "responses": {
                        "200": {"description": "Client summary"},
                        "404": {"description": "Client not found"},
                    },
                }
            },
            "/clients/{client_id}/workouts": {
                "get": {
                    "summary": "List workouts for a client",
                    "parameters": [{"$ref": "#/components/parameters/ClientId"}],
                    "responses": {
                        "200": {"description": "Workout list"},
                        "404": {"description": "Client not found"},
                    },
                },
                "post": {
                    "summary": "Create a workout for a client",
                    "parameters": [{"$ref": "#/components/parameters/ClientId"}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/WorkoutInput"}
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Workout created"},
                        "400": {"description": "Validation error"},
                        "404": {"description": "Client not found"},
                    },
                },
            },
        },
        "components": {
            "parameters": {
                "ClientId": {
                    "name": "client_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer", "minimum": 1},
                }
            },
            "schemas": {
                "Health": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string"},
                        "status": {"type": "string", "example": "ok"},
                    },
                },
                "Program": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "focus": {"type": "string"},
                        "weekly_plan": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "target_calories": {"type": "integer"},
                    },
                },
                "Client": {
                    "allOf": [
                        {"$ref": "#/components/schemas/ClientInput"},
                        {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}},
                        },
                    ]
                },
                "ClientInput": {
                    "type": "object",
                    "required": ["name", "age", "height_cm", "weight_kg"],
                    "properties": {
                        "name": {"type": "string", "example": "Asha Kumar"},
                        "age": {"type": "integer", "example": 29},
                        "height_cm": {"type": "number", "example": 168},
                        "weight_kg": {"type": "number", "example": 66},
                        "program": {
                            "type": "string",
                            "enum": ["Fat Loss", "Muscle Gain", "Beginner"],
                            "example": "Fat Loss",
                        },
                        "membership_end": {
                            "type": "string",
                            "format": "date",
                            "example": "2999-12-31",
                        },
                    },
                },
                "WorkoutInput": {
                    "type": "object",
                    "required": ["workout_type", "duration_min"],
                    "properties": {
                        "date": {
                            "type": "string",
                            "format": "date",
                            "example": "2026-10-10",
                        },
                        "workout_type": {"type": "string", "example": "Strength"},
                        "duration_min": {"type": "integer", "example": 60},
                        "notes": {
                            "type": "string",
                            "example": "Squat and bench session",
                        },
                    },
                },
            },
        },
    }
