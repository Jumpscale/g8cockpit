## Service Templates

In the **Templates** page you get an overview of all AYS service templates available in the Cockpit:

![](templates.png)

Here you can filter on the name of the **repository** where the template is available, or on the **name** of the service template:

![](filter-on-template-name.png)

Clicking the name of the service template leads you to the service **Template Details** page:

![](service-template-info.png)

Under **schema.hrd** you see the attributes for describing a service instance of the service template type:

![](schema.png)

Under **actions.py** you see the implementation of all actions available for service instances of the service template type.

Here for the VDC service template for actions are implemented:

- init()
  ![](init.png)

- install()
  ![](install.png)

- uninstall()
  ![](uninstall.png)

- getClient()
  ![](getClient.png)

  At the bottom of the page there is an overview of all service instances based on this service template:

  ![]()
