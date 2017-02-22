package ihart;

import ihart.CVEvent.EVENT_TYPE;

/**
 * Blob is a simple object which provides getters and allows the user to access
 * the information for a particular blob.
 **/
public class Blob {

	/**
	 * Fields
	 **/
	private double xCoor;
	private double yCoor;
	private double bWidth;
	private double bHeight;
	private CVEvent.EVENT_TYPE type;
	private int roi; // region of interest where this blob occurred

	/**
	 * Constructor sets all properties for a blob
	 *
	 * @param eventType
	 *            The type of the blob
	 * @param xCoor
	 *            The x coordinate of the top left of the blob
	 * @param yCoord
	 *            The y coordinate of the top left of the blob
	 * @param width
	 *            The width of the blob
	 * @param height
	 *            The height of the blob
	 *
	 **/
	public Blob(CVEvent.EVENT_TYPE eventType, double xCoor, double yCoord, double width, double height, int roi) {
		this.xCoor = xCoor;
		this.yCoor = yCoord;
		this.bWidth = width;
		this.bHeight = height;
		type = eventType;
		this.roi = roi;
	}

	/**
	 * @return The x coordinate for the top left of the blob
	 **/
	public double getX() {
		return xCoor;
	}

	/**
	 * @return The y coordinate for the top left of the blob
	 **/
	public double getY() {
		return yCoor;
	}

	/**
	 * @return The width of the blob
	 **/
	public double getWidth() {
		return bWidth;
	}

	/**
	 * @return The height of the blob
	 **/
	public double getHeight() {
		return bHeight;
	}

	/**
	 * @return The type of the blob
	 **/
	public EVENT_TYPE getType() {
		return type;
	}

	/**
	 * Get region of interest index return roi
	 **/
	public int getROI() {
		return roi;
	}
}
