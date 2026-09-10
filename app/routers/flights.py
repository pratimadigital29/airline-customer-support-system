"""Flight status + booking lookup (PSS/GDS adapters in production)."""

from fastapi import APIRouter, HTTPException

from app.schemas import BookingOut, FlightOut
from app.services import knowledge

router = APIRouter(tags=["flights"])


@router.get("/flights", response_model=list[FlightOut])
def list_flights(origin: str = "", destination: str = "", status: str = ""):
    return knowledge.search_flights(origin=origin, destination=destination, status=status)


@router.get("/flights/{flight_no}", response_model=FlightOut)
def flight_status(flight_no: str):
    flight = knowledge.get_flight(flight_no)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.get("/bookings/{pnr}", response_model=BookingOut)
def booking_lookup(pnr: str):
    booking = knowledge.get_booking(pnr)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
